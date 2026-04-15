import requests
import json
import sys

class OllamaClient:
    """Client for interacting with Ollama API"""
    
    def __init__(self, model_name="llama3.1:8b"):
        self.model = model_name
        self.api_base = "http://localhost:11434/api"
        self.chat_url = f"{self.api_base}/chat"
        self.tags_url = f"{self.api_base}/tags"
    
    def stream_chat(self, messages):
        """Send messages to model and stream the response"""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True
        }

        try:
            response = requests.post(self.chat_url, json=payload, stream=True)
            response.raise_for_status()

            full_response = ""
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    if 'message' in chunk:
                        content = chunk['message'].get('content', '')
                        full_response += content
                        print(content, end='', flush=True)
                    if chunk.get('done', False):
                        print()  # New line
                        break

            return full_response.strip()

        except requests.exceptions.RequestException as e:
            print("建议检查模型型号是否正确，或ollama是否打开")
            print(f"错误: {str(e)}")
            return None
    
    def load_model(self):
        """Preload the selected model"""
        return requests.post(self.chat_url, json={"model": self.model})
    
    def get_available_models(self):
        """Get list of available models"""
        response = requests.get(self.tags_url)
        return response.json()


class ChatInterface:
    EXIT_COMMANDS = ['quit', 'exit', 'goodbye', 'bye', 'see you', 'later', 'farewell',
                    '再见', '拜拜', '下次见', '回头见', '走了', '告辞']
    
    def __init__(self):
        self.client = None
    
    def choose_model(self):
        while True:
            print("\n请选择模型类型:")
            print("1. 默认推理模型（qwen3:latest）")
            print("2. 默认通用模型 （llama3.1:8b）")
            print("3. 高级")
            print("4. 默认最强通用模型 (phi4:latest)")
            print("5. 退出")
            
            category_choice = input("请输入类型 (1-5): ")
            
            if category_choice == '1':
                return "qwen3:latest"
            elif category_choice == '2':
                return "llama3.1:8b"
            elif category_choice == '4':
                return "phi4:latest"
            elif category_choice == '3':
                # Create temporary client to get model list
                temp_client = OllamaClient()
                models_data = temp_client.get_available_models()
                models_list = models_data['models']
                
                print("可用模型列表:")
                for i, model in enumerate(models_list):
                    print(f"{i + 1}. {model['name']} - {model['details']['parameter_size']}")
                
                exit_option = len(models_list) + 1
                print(f"{exit_option}. 退出")
                
                try:
                    choose_model_num = int(input("请输入模型编号: "))
                    
                    if 1 <= choose_model_num <= len(models_list):
                        model = models_list[choose_model_num - 1]
                        print(f"您选择的模型是: {model['name']}")
                        
                        # Display model info
                        print("模型信息:")
                        print(f"名称: {model['name']}")
                        print(f"模型大小: {model['details']['parameter_size']}")
                        
                        if model['name'] == 'snowflake-arctic-embed2:latest':
                            print("该模型为嵌入模型，无法使用对话")
                            print("该模型为嵌入模型，无法使用对话")
                            print("该模型为嵌入模型，无法使用对话")
                        
                        more_info = input("是否需要更多信息？(y/n): ")
                        if more_info.lower() == 'y':
                            details = model["details"]
                            print(f"模型修改时间: {model['modified_at']}")
                            print(f"模型标签: {model['digest']}")
                            for key, value in details.items():
                                print(f"  - {key}: {value}")
                        
                        confirm = input("是否确认使用该模型？(y/n): ")
                        if confirm.lower() == 'y':
                            return model['name']
                        else:
                            print("请重新选择模型")
                            continue
                    elif choose_model_num == exit_option:
                        print("感谢使用，再见！")
                        sys.exit(0)
                    else:
                        print("无效选择，请重试")
                        continue
                except ValueError:
                    print("请输入有效数字")
                    continue
            elif category_choice == '5':
                print("感谢使用，再见！")
                sys.exit(0)
            else:
                print("无效选择，请重试")
                continue
                
        return "qwen3:latest"  # Default fallback
    
    def run_chat_session(self):
        model_name = self.choose_model()
        self.client = OllamaClient(model_name)
        
        print("\n\n欢迎使用 Ollama 聊天助手")
        print(f"正在载入模型: {model_name}")
        print("请稍等...")
        
        self.client.load_model()
        print("输入 'quit' 或 'exit' 结束对话")
        
        conversation = []
        is_conversation_end = False
        
        while True:
            user_input = input("\n您: ")
            if user_input.lower() in self.EXIT_COMMANDS:
                is_conversation_end = True
                
            conversation.append({"role": "user", "content": user_input})
            print("\nAI: ", end='', flush=True)
            
            ai_response = self.client.stream_chat(conversation)
            if ai_response:
                conversation.append({"role": "assistant", "content": ai_response})
                
            if is_conversation_end:
                break


def main():
    chat = ChatInterface()
    chat.run_chat_session()


if __name__ == "__main__":
    main()
