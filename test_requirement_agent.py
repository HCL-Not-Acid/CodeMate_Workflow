from agents.requirement_agent import RequirementAgent


agent = RequirementAgent()

requirement = """
做一个学生成绩统计工具。
"""

print("正在进行需求分析……")

result = agent.run(requirement)

print("\n========== 需求分析结果 ==========\n")
print(result)