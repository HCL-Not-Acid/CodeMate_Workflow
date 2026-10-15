import os  #读取电脑里的环境变量
from dotenv import load_dotenv  #负责读取.env

load_dotenv()  #把.env文件里的配置加载进Python

API_KEY = os.getenv("DASHSCOPE_API_KEY")

BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

MODEL_NAME = "qwen-plus"