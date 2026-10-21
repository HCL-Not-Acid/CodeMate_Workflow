import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from workflow import SimpleWorkflow


class SimpleWorkflowTests(unittest.TestCase):
    def test_agents_run_in_order_and_share_results(self):
        with (
            patch("workflow.validate_config"),
            patch("workflow.RequirementAgent") as requirement_agent,
            patch("workflow.DesignAgent") as design_agent,
            patch("workflow.CodingAgent") as coding_agent,
        ):
            requirement_agent.return_value.run.return_value = "parsed requirements"
            design_agent.return_value.run.return_value = "design plan"
            coding_agent.return_value.run.return_value = "print('ok')"
            workflow = SimpleWorkflow()

            with redirect_stdout(io.StringIO()):
                state = workflow.run("make a small program")

        self.assertEqual(state["status"], "completed")
        self.assertEqual(state["current_stage"], "完成")
        self.assertEqual(state["requirement_analysis"], "parsed requirements")
        self.assertEqual(state["design_plan"], "design plan")
        self.assertEqual(state["generated_code"], "print('ok')")
        requirement_agent.return_value.run.assert_called_once_with(
            "make a small program"
        )
        design_agent.return_value.run.assert_called_once_with(
            "parsed requirements"
        )
        coding_agent.return_value.run.assert_called_once_with(
            "make a small program", "parsed requirements", "design plan"
        )
        self.assertEqual(
            list(state["stage_timings"]), ["需求分析", "方案设计", "代码生成"]
        )
        self.assertTrue(all(value >= 0 for value in state["stage_timings"].values()))
        self.assertEqual(state["stage_errors"], {})

    def test_stage_failure_is_recorded_and_stops_later_agents(self):
        with (
            patch("workflow.validate_config"),
            patch("workflow.RequirementAgent") as requirement_agent,
            patch("workflow.DesignAgent") as design_agent,
            patch("workflow.CodingAgent") as coding_agent,
        ):
            requirement_agent.return_value.run.return_value = "parsed requirements"
            design_agent.return_value.run.side_effect = RuntimeError("model unavailable")
            workflow = SimpleWorkflow()

            with redirect_stdout(io.StringIO()):
                state = workflow.run("make a small program")

        self.assertEqual(state["status"], "failed")
        self.assertEqual(state["current_stage"], "方案设计")
        self.assertIn("方案设计阶段失败", state["error"])
        self.assertEqual(state["stage_errors"], {"方案设计": "model unavailable"})
        self.assertEqual(list(state["stage_timings"]), ["需求分析", "方案设计"])
        coding_agent.return_value.run.assert_not_called()

    def test_invalid_generated_python_is_reported_as_coding_failure(self):
        with (
            patch("workflow.validate_config"),
            patch("workflow.RequirementAgent") as requirement_agent,
            patch("workflow.DesignAgent") as design_agent,
            patch("workflow.CodingAgent") as coding_agent,
        ):
            requirement_agent.return_value.run.return_value = "parsed requirements"
            design_agent.return_value.run.return_value = "design plan"
            coding_agent.return_value.run.return_value = "def broken(:"
            workflow = SimpleWorkflow()

            with redirect_stdout(io.StringIO()):
                state = workflow.run("make a small program")

        self.assertEqual(state["status"], "failed")
        self.assertEqual(state["current_stage"], "代码生成")
        self.assertIn("语法错误", state["stage_errors"]["代码生成"])
        self.assertIn("代码生成", state["stage_timings"])


if __name__ == "__main__":
    unittest.main()
