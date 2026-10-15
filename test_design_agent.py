from agents.requirement_agent import RequirementAgent
from agents.design_agent import DesignAgent


# 用户提出的原始需求
user_requirement = """
请开发一个 Python 命令行程序。

1. 用户逐个输入学生成绩，每次输入一个成绩。
2. 输入空行时结束录入。
3. 程序计算并显示平均分、最高分和最低分。
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


# 输出完成提示
print("\n========== 两个 Agent 执行完成 ==========")