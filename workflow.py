import ast
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Callable

from config import validate_config
from agents.requirement_agent import RequirementAgent
from agents.design_agent import DesignAgent
from agents.coding_agent import CodingAgent


@dataclass(frozen=True)
class WorkflowStage:
    """描述一个工作流阶段及其输出状态字段。"""

    name: str
    output_key: str
    run: Callable[[dict], str]


class SimpleWorkflow:
    """按阶段配置顺序执行 Agent，并通过共享状态传递结果。"""

    def __init__(self, stages=None):
        """创建默认流程；也可传入自定义的有序阶段列表。"""

        if stages is None:
            validate_config()
            self.requirement_agent = RequirementAgent()
            self.design_agent = DesignAgent()
            self.coding_agent = CodingAgent()
            self.stages = self._build_stages()
        else:
            self.stages = list(stages)

        if not self.stages:
            raise ValueError("工作流至少需要配置一个阶段。")

    def _build_stages(self):
        """集中配置默认阶段，调整流程时无需改动 run() 主循环。"""

        return [
            WorkflowStage(
                name="需求分析",
                output_key="requirement_analysis",
                run=lambda state: self.requirement_agent.run(
                    state["user_requirement"]
                ),
            ),
            WorkflowStage(
                name="方案设计",
                output_key="design_plan",
                run=lambda state: self.design_agent.run(
                    state["requirement_analysis"]
                ),
            ),
            WorkflowStage(
                name="代码生成",
                output_key="generated_code",
                run=self._generate_code,
            ),
        ]

    def run(self, user_requirement):
        """按顺序执行三个 Agent，并通过共享状态保存结果。"""

        # 共享状态：记录原始需求和各阶段的输出
        state = {
            "user_requirement": user_requirement,
            "requirement_analysis": "",
            "design_plan": "",
            "generated_code": "",
            "current_stage": "准备开始",
            "status": "running",
            "error": None,
            "stage_timings": {},
            "stage_errors": {},
        }

        try:
            for index, stage in enumerate(self.stages, start=1):
                state["current_stage"] = stage.name
                print(f"\n========== 第{index}阶段：{stage.name} ==========\n")
                stage_started = perf_counter()
                try:
                    result = stage.run(state)
                    if not isinstance(result, str) or not result.strip():
                        raise ValueError(f"{stage.name} Agent 未返回有效内容。")

                    state[stage.output_key] = result
                    print(result)
                except Exception as error:
                    state["stage_errors"][stage.name] = str(error)
                    raise
                finally:
                    elapsed = perf_counter() - stage_started
                    state["stage_timings"][stage.name] = elapsed
                    outcome = "失败" if stage.name in state["stage_errors"] else "完成"
                    print(f"[{stage.name}] {outcome}，耗时 {elapsed:.2f} 秒。")

            state["status"] = "completed"
            state["current_stage"] = "完成"

        except Exception as error:
            state["status"] = "failed"
            state["error"] = (
                f"{state['current_stage']}阶段失败：{error}"
            )

        return state

    def _generate_code(self, state):
        """运行代码生成阶段并检查生成代码的语法。"""

        code = self.coding_agent.run(
            state["user_requirement"],
            state["requirement_analysis"],
            state["design_plan"],
        )
        code = self._clean_code(code)

        try:
            ast.parse(code, filename="generated_program.py")
        except SyntaxError as error:
            raise ValueError(
                f"生成代码存在语法错误，第 {error.lineno} 行：{error.msg}"
            ) from error

        return code

    @staticmethod
    def _clean_code(code):
        """去除代码前后的 Markdown 围栏。"""

        code = code.strip()

        if code.startswith("```"):
            lines = code.splitlines()

            # 删除第一行，例如 ```python
            lines = lines[1:]

            # 删除末尾的 ```
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            code = "\n".join(lines).strip()

        return code


def read_user_requirement():
    """读取用户输入的多行软件需求。"""

    print("请输入你想开发的软件需求。")
    print("输入完成后，直接按回车提交空行即可开始执行。\n")

    lines = []

    while True:
        line = input()

        if not line.strip():
            break

        lines.append(line)

    return "\n".join(lines).strip()


def main():
    """工作流的程序入口。"""

    user_requirement = read_user_requirement()

    if not user_requirement:
        print("未输入软件需求，工作流结束。")
        return

    try:
        workflow = SimpleWorkflow()
    except ValueError as error:
        print(f"\n配置错误：{error}")
        return

    state = workflow.run(user_requirement)

    if state["status"] != "completed":
        print("\n========== 工作流执行失败 ==========")
        print(state["error"])
        print("请根据报错检查对应阶段，修复后重新运行。")
        return

    # 将最终代码保存到文件
    output_path = Path("generated_program.py")

    try:
        output_path.write_text(
            state["generated_code"] + "\n",
            encoding="utf-8",
        )
    except OSError as error:
        print(f"\n代码已经生成，但保存文件失败：{error}")
        return

    print("\n========== 工作流执行成功 ==========")
    print(f"生成的代码已保存到：{output_path.resolve()}")


if __name__ == "__main__":
    main()
