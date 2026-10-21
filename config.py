import os  #读取电脑里的环境变量
from dotenv import load_dotenv  #负责读取.env

load_dotenv()  #把.env文件里的配置加载进Python

API_KEY = os.getenv("DASHSCOPE_API_KEY")

BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

MODEL_NAME = "qwen-plus"


def validate_config():
    """检查模型调用所需配置，并用中文说明缺失项。"""

    if not API_KEY or not API_KEY.strip():
        raise ValueError(
            "未检测到阿里云百炼 API Key。请在项目根目录的 .env 文件中设置 "
            "DASHSCOPE_API_KEY 后重试。"
        )
