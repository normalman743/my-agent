# models/LLM/ollama_client.py
import json
import requests
from tqdm import tqdm
import sys
import time  # 模拟加载时间
from models.LLM.base_client import BaseLLMClient
from app.utils.code_executor import execute_python
from app.utils.search_engine import SearchEngine
from app.utils.terminal import execute_command
from config.tools import get_tools_for_model, get_tool_details
from models.LLM.run_ollama import check_ollama
def parse_message(message):
    # 从消息中提取内容
    content = message.get('content', '')
    
    # 检查内容是否以 <|python_tag|> 开头
    if content.startswith('<|python_tag|'):
        # 提取 JSON 部分并解析
        try:
            json_content = content[len('<|python_tag|'):].strip()
            parameters = json.loads(json_content).get('parameters', {})
            return True, parameters
        except json.JSONDecodeError:
            return False, content
    else:
        return False, content

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
        payload1 = json.dumps({"model": self.model_name})
        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.post(url, headers=headers, data=payload1)
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
        payload2 = {
            "model": self.model_name,
            "prompt": prompt
        }
        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.post(self.api_url, json=payload2, headers=headers)
            response.raise_for_status()
            result = response.json()
            return result.get('response', '')
        except requests.exceptions.RequestException as e:
            print(f"生成响应时发生错误: {str(e)}")
            return ''

    def handle_tool_call(self, tool_call, conversation):
        if tool_call['function']['name'] == 'terminal':
            arguments = json.loads(tool_call['function']['arguments'])
            code = arguments['code']
            execution_authority = arguments['execution_authority']
            
            if execution_authority == 'general':
                result = "You don't have the required permissions."
            else:
                result = execute_command(code)
            
            reply = {
                "role": "ipython",
                "content": json.dumps({"output": result})
            }
            conversation.append(reply)
        return conversation
    
    def send_request(self, conversation):
        payload3 = {
            "model": self.model_name,
            "messages": conversation,
            "stream": True,
            "tools": [{
                "type": "function",
                "function": {
                    "name": "terminal",
                    "description": "Execute terminal commands",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "The command to be executed in the terminal"
                            },
                            "execution_authority": {
                                "type": "string",
                                "enum": ["general", "sudo"],
                                "description": "The execution authority level for the command"
                            }
                        },
                        "required": ["code", "execution_authority"]
                    }
                }
            }]
        }
        return requests.post(self.api_url, json=payload3, stream=True)

    def chat_with_llm(self, conversation):
        """与模型进行对话"""
        print(f"conversation is {conversation}")
        payload4 = {
            "model": self.model_name,
            "messages": conversation,
            "stream": True,
        }
        try:
            response = requests.post(self.api_url, json=payload4, stream=True)
            response.raise_for_status()
            full_response = ""
            for line in response.iter_lines():
                if line:
                    json_response = json.loads(line)
                    if 'message' in json_response:
                        content = json_response['message'].get('content', '')                   
                        full_response += content
                        yield content
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            yield f"An error occurred: {str(e)}"


"""

if 'tool_calls' in json_response['message']:
                            # Check if the tool is terminal

                            
                            if json_response['message']['tool_calls']['function']['name'] == 'terminal':
                                tool_call = json_response['message']['tool']['function']
                                code = tool_call['arguments']['arguments']['code']
                                execution_authority = tool_call['arguments']['arguments']['execution_authority']
                                
                                if execution_authority == 'general':
                                    result = "You don't have the required permissions."
                                else:
                                    result = execute_command(code)
                                
                                reply = {
                                    "role": "ipython",
                                    "content": json.dumps({"output": result})
                                }
                                conversation.append(reply)
                                payload4 = {
                                    "model": self.model_name,
                                    "messages": conversation,
                                    "stream": True,
                                }
                                response = requests.post(self.api_url, json=payload4, stream=True)
                                response.raise_for_status()
                                for line in response.iter_lines():
                                    if line:
                                        json_response = json.loads(line)
                                        if 'message' in json_response:
                                            content = json_response['message'].get('content', '')

                                            
"""