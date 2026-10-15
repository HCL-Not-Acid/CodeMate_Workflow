from pathlib import Path

from agents.requirement_agent import RequirementAgent
from agents.design_agent import DesignAgent
from agents.coding_agent import CodingAgent


class SimpleWorkflow:
    """管理需求分析、方案设计和代码生成三个阶段。"""

    def __init__(self):
        # 创建三个 Agent
        self.requirement_agent = RequirementAgent()
        self.design_agent = DesignAgent()
        self.coding_agent = CodingAgent()

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
        }

        try:
            # 第一阶段：需求分析
            state["current_stage"] = "需求分析"
            print("\n========== 第一阶段：需求分析 ==========\n")

            state["requirement_analysis"] = (
                self.requirement_agent.run(user_requirement)
            )

            if not state["requirement_analysis"].strip():
                raise ValueError("需求分析 Agent 未返回有效内容。")

            print(state["requirement_analysis"])

            # 第二阶段：方案设计
            state["current_stage"] = "方案设计"
            print("\n========== 第二阶段：方案设计 ==========\n")

            state["design_plan"] = self.design_agent.run(
                state["requirement_analysis"]
            )

            if not state["design_plan"].strip():
                raise ValueError("设计 Agent 未返回有效内容。")

            print(state["design_plan"])

            # 第三阶段：代码生成
            state["current_stage"] = "代码生成"
            print("\n========== 第三阶段：代码生成 ==========\n")

            state["generated_code"] = self.coding_agent.run(
                state["user_requirement"],
                state["requirement_analysis"],
                state["design_plan"],
            )

            if not state["generated_code"].strip():
                raise ValueError("编码 Agent 未返回有效代码。")

            # 去除模型偶尔返回的 Markdown 代码围栏
            state["generated_code"] = self._clean_code(
                state["generated_code"]
            )

            print(state["generated_code"])

            state["status"] = "completed"
            state["current_stage"] = "完成"

        except Exception as error:
            state["status"] = "failed"
            state["error"] = (
                f"{state['current_stage']}阶段失败：{error}"
            )

        return state

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

    workflow = SimpleWorkflow()
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
