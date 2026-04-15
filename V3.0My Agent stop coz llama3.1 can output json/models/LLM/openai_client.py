# models/LLM/openai_client.py
import openai
from config.config import config  
from models.LLM.base_client import BaseLLMClient
import requests

class OpenAIClient(BaseLLMClient):
    def __init__(self, model_name="gpt-4o-mini"):
        self.model_name = model_name
        self.api_key = config['apis']['OPENAI_API_KEY']  # 从配置文件加载 API 密钥
        openai.api_key = self.api_key

    def _load_model(self):
        """加载模型"""
        print(f"模型 {self.model_name} 已准备好使用（无需显式加载）。")

    def generate_response(self, prompt: str) -> str:
        """根据提示生成响应"""
        try:
            response = openai.Completion.create(
                model=self.model_name,
                prompt=prompt,
                max_tokens=500  # 根据需要设置生成的最大 token 数量
            )
            return response.choices[0].text.strip()
        except requests.exceptions.RequestException as e:  # 捕获 HTTP 请求异常
            print(f"生成响应时发生网络错误: {str(e)}")
            return ''
        except Exception as e:
            print(f"生成响应时发生未知错误: {str(e)}")
            return ''

    def chat_with_llm(self, conversation):
        """与模型进行对话"""
        formatted_conversation = "\n".join([f"{message['role']}: {message['content']}" for message in conversation])
        print(formatted_conversation)

        try:
            messages = [
                {"role": "system", "content": "You are a helpful assistant."}
            ] + conversation  # 包含系统消息

            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=messages,
                max_tokens=500,  # 调整根据需要的 token 限制
                stream=True  # 启用流式响应
            )

            full_response = ""
            for chunk in response:
                if chunk['choices'][0]['finish_reason'] is None:
                    content = chunk['choices'][0]['delta'].get('content', '')
                    full_response += content
                    print(content, end='', flush=True)  # 实时打印响应

            return "reply", full_response.strip()

        except requests.exceptions.RequestException as e:  # 捕获 HTTP 请求异常
            return "error", f"网络请求错误: {str(e)}"
        except Exception as e:  # 捕获其他所有异常
            return "error", f"未知错误: {str(e)}"
