# models/LLM/ollama_client.py
import json
import requests
from tqdm import tqdm
import sys
import time  # 模拟加载时间
from models.LLM.base_client import BaseLLMClient
from app.utils.code_executor import execute_python
from app.utils.search_engine import SearchEngine
from config.tools import get_tools_for_model, get_tool_details
from models.LLM.run_ollama import check_ollama

class OllamaClient(BaseLLMClient):
    def __init__(self, model_name="llama3.1:8b"):
        print("正在初始化 Ollama 客户端...")
        check_ollama(modelname=model_name)
        self.model_name = model_name
        self.api_url = "http://localhost:11434/api/chat"  # Ollama 默认 API 地址
        self._load_model()

    def _call_tool(self, tool_name, **tool_params):
        if tool_name == "execute_python":
            code = tool_params.get("code", "")
            security_level = tool_params.get("security_level", 1)
            return execute_python(code, security_level)
        elif tool_name == "search":
            query = tool_params.get("query", "")
            return SearchEngine().search(query)
        else:
            return "不支持的工具名称"
    def manage_tools(self):
        # 获取该模型适用的工具列表
        tools = get_tools_for_model(self.model_name)
        # 查询每个工具的详细信息
        tool_details = [get_tool_details(tool) for tool in tools]
        return tool_details

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
            sys.exit(1) 

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
        """与模型进行对话"""
        formatted_conversation = json.dumps(conversation, indent=4, ensure_ascii=False)
        print(formatted_conversation)

        payload = {
            "model": self.model_name,
            "messages": conversation,
            "stream": True,  # 启用流式响应
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "terminal",
                        "description": "Execute commands in terminal and return the result almost everything you can do in terminal",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "command": {
                                    "type": "string",
                                    "description": "The terminal command to execute"
                                }
                            },
                            "required": ["command"]
                        }
                    }
                }
            ]
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
                        if 'tool' in json_response['message']:
                            tool_name = json_response['message']['tool']['name']
                            tool_params = json_response['message']['tool']['parameters']
                            tool_result = self._call_tool(tool_name, **tool_params)
                            content += f"\n\nTool 执行结果: {tool_result}"
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