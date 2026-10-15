from pathlib import Path

from agents.requirement_agent import RequirementAgent
from agents.design_agent import DesignAgent
from agents.coding_agent import CodingAgent


# 用户原始需求
user_requirement = """
请开发一个 Python 命令行程序。

1. 用户逐个输入学生成绩，每次输入一个成绩。
2. 输入空行时结束录入。
3. 程序在录入结束后计算并显示平均分、最高分和最低分。
4. 平均分保留两位小数。
5. 如果没有输入任何成绩，应显示提示信息。
6. 不需要把成绩保存到文件。
"""


# 第一阶段：需求分析
print("\n========== 第一阶段：需求分析 ==========\n")

requirement_agent = RequirementAgent()
requirement_result = requirement_agent.run(user_requirement)

print(requirement_result)


# 第二阶段：方案设计
print("\n========== 第二阶段：方案设计 ==========\n")

design_agent = DesignAgent()
design_result = design_agent.run(requirement_result)

print(design_result)


# 第三阶段：代码生成
print("\n========== 第三阶段：代码生成 ==========\n")

coding_agent = CodingAgent()

code_result = coding_agent.run(
    user_requirement,
    requirement_result,
    design_result
)

print(code_result)


# 将生成的代码保存到文件
code = code_result.strip()

# 兼容模型偶尔返回 Markdown 代码围栏的情况
if code.startswith("```"):
    lines = code.splitlines()

    if lines and lines[0].startswith("```"):
        lines = lines[1:]

    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]

    code = "\n".join(lines).strip()

output_path = Path("generated_program.py")
output_path.write_text(code + "\n", encoding="utf-8")

print("\n========== 代码生成完成 ==========")
print(f"生成的代码已保存到：{output_path.resolve()}")