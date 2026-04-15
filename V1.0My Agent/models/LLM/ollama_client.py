# models/LLM/ollama_client.py
import json
import requests
from tqdm import tqdm
import time  # 模拟加载时间
from abc import ABC, abstractmethod
from models.LLM.base_client import BaseLLMClient

DEFAULT_PROMPT = """
你是一个易经解释器，会根据不同的问题以及卦象、卦辞给出不同的解释。你会收到 本卦（目前状态），变卦（变化状态或无），以及变化了的阴阳艾词，并给出解释
"""

    def __init__(self, model_name="llama3.1:8b"):
        self.model_name = model_name
        self.api_url = "http://localhost:11434/api/chat"  # Ollama 默认 API 地址
        self._load_model()

    def _load_model(self):
        """加载模型"""
        print(f"你正在使用本地模型{self.model_name}")
        
        print("正在载入模型，请稍等...")
        url = "http://localhost:11434/api/generate"
        payload = json.dumps({"model": self.model_name})
        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()
            result = response.json()
            if result.get("done"):
                print(f"模型 {self.model_name} 已成功加载!")
            else:
                print(f"模型 {self.model_name} 加载失败。")
        except requests.exceptions.RequestException as e:
            print(f"加载模型时发生错误: {str(e)}")

    def generate_response(self, prompt: str) -> str:
        """根据提示生成响应"""
        payload = {
            "model": self.model_name,
            "prompt": prompt
        }
        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.post(self.api_url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            return result.get('response', '')
        except requests.exceptions.RequestException as e:
            print(f"生成响应时发生错误: {str(e)}")
            return ''

    def chat_with_llm(self, conversation):

        formatted_conversation = json.dumps(conversation, indent=4, ensure_ascii=False)
        print(formatted_conversation)

        """与模型进行对话"""
        payload = {
            "model": self.model_name,
            "messages": conversation,
            "stream": True,  # 启用流式响应
        }

        try:
            response = requests.post(self.api_url, json=payload, stream=True)
            response.raise_for_status()
            full_response = ""
            for line in response.iter_lines():
                if line:
                    json_response = json.loads(line)
                    if 'message' in json_response:
                        content = json_response['message'].get('content', '')
                        full_response += content
                        print(content, end='', flush=True)  # 实时打印响应
                    if json_response.get('done', False):
                        break

            try:
                ai_response = json.loads(full_response)
                status = ai_response.get("status", "reply")
                message = ai_response.get("message", full_response)
            except json.JSONDecodeError:
                status = "reply"
                message = full_response

            return status, message

        except requests.exceptions.RequestException as e:
            return "error", str(e)
