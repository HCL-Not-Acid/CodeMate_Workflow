from openai import OpenAI
from config import API_KEY, BASE_URL, MODEL_NAME


class ModelAgent:
    """专门 Agent 的公共基础类，负责调用大模型。"""

    def __init__(self, system_prompt):
        self.client = OpenAI(
            api_key=API_KEY,
            base_url=BASE_URL
        )

        self.system_prompt = system_prompt

    def run(self, user_input):
        """接收任务，调用大模型，并返回回答。"""

        response = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        )

        return response.choices[0].message.content