import requests
import json
import sys
import time
def take_part_of_conversation(conversation):
    """Take part of the conversation if <think> ... </think> in conversation return think part and after think part"""
    if "<think>" in conversation:
        start = conversation.index("<think>") + len("<think>")
        end = conversation.index("</think>")
        think_part = conversation[start:end]
        after_think_part = conversation[end + len("</think>"):]
        return think_part, after_think_part
    else:
        return None, conversation

class OllamaClient:
    """Client for interacting with Ollama API"""
    
    def __init__(self, model_name="llama3.1:8b"):
        self.model = model_name
        self.api_base = "http://localhost:11434/api"
        self.chat_url = f"{self.api_base}/chat"
        self.tags_url = f"{self.api_base}/tags"
        self.ifchat = False
        self.image = []

    def inputbase64bypath(self, image_path):
        """Convert image file to base64 string with format validation"""
        import base64
        import os
        
        # 支持的图像格式
        SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        
        try:
            # 检查文件是否存在
            if not os.path.exists(image_path):
                print(f"错误: 文件不存在 - {image_path}")
                return 0
                
            # 检查文件扩展名
            file_ext = os.path.splitext(image_path)[1].lower()
            if file_ext not in SUPPORTED_FORMATS:
                print(f"警告: 不支持的文件格式 {file_ext}，支持的格式: {', '.join(SUPPORTED_FORMATS)}")
                
            # 读取图像文件并转换为base64
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
                
                # 检查文件是否为空
                if len(image_data) == 0:
                    print("错误: 文件为空")
                    return 0
                    
                # Convert image to base64 and append to image list
                base64_image = base64.b64encode(image_data).decode('utf-8')
                self.image.append(base64_image)
                print(f"成功: 图像文件已转换为base64 ({len(base64_image)} 字符)")
                return 1
                
        except FileNotFoundError:
            print(f"错误: 无法找到文件 - {image_path}")
            return 0
        except PermissionError:
            print(f"错误: 没有权限读取文件 - {image_path}")
            return 0
        except Exception as e:
            print(f"错误: 处理图像文件时出现问题 - {str(e)}")
            return 0
    
    def getscreenshotinfo(self):
        """Get screenshot and analyze it with AI"""
        import pyautogui
        import os
        import time
        
        try:
            # 生成带时间戳的文件名，避免覆盖
            timestamp = int(time.time())
            screenshot_path = f"screenshot_{timestamp}.png"
            
            print("正在截取屏幕...")
            screenshot = pyautogui.screenshot()
            screenshot.save(screenshot_path)
            print(f"截图已保存到 {screenshot_path}")
            
            # 获取图像分析结果
            result = self.getimageinfo(screenshot_path)
            
            # 可选：询问是否保留截图文件
            keep_file = 'y'
            if keep_file != 'y':
                try:
                    os.remove(screenshot_path)
                    print(f"截图文件 {screenshot_path} 已删除")
                except OSError as e:
                    print(f"警告: 无法删除截图文件 - {str(e)}")
            
            return result
            
        except Exception as e:
            print(f"错误: 截图过程中出现问题 - {str(e)}")
            return None

    def getimageinfo(self,image_path,stream=False,prompy = "用户在做什么？请用json回答 \napp：\ndescription：\n」\n注意description应该在10-20字"):
        """Get image info from the image path"""
        if self.inputbase64bypath(image_path) == 0:
            return None
        else:
            # 使用 Generate API 而不是 Chat API
            generate_url = f"{self.api_base}/generate"
            payload = {
                "model": self.model,
                "prompt": prompy,
                "stream": stream,
                "system": "你是一个AI助手，你的任务是分析屏幕截图并提供详细描述。",
                "images": self.image,
                "format": "json"
            }
            if stream:
                print("我们还不支持流式图像分析，请使用非流式模式")
            else:
                try:
                    response = requests.post(generate_url, json=payload)
                    response.raise_for_status()
                    result = response.json()
                    print(f"AI 分析结果: {result.get('response', '无响应')}")
                    return result
                except requests.exceptions.RequestException as e:
                    print(f"错误: {str(e)}")
                    return None
        
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
        self.ifchat = False
    
    def choose_model(self):
        while True:
            print("\n请选择模型类型:")
            print("1. 默认推理模型（qwen3:latest）")
            print("2. 默认通用模型 （llama3.1:8b）")
            print("3. 高级")
            print("4. 默认最强通用模型 (phi4:latest)")
            print("5. 退出")
            if not self.ifchat: print("6. 大模型彼此对话")
            
            category_choice = input("请输入类型: ")
            
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
            elif category_choice == '6':
                if self.ifchat:
                    print("已经在对话模式中")
                    continue
                self.llm_conversation()
                continue
            else:
                print("无效选择，请重试")
                continue
                
    
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

    def llm_conversation(self, num_exchanges=5):
        """Have two LLM models converse with each other"""
        self.ifchat = True
        print("\n=== LLM 对话模式 ===")
        print("在此模式下，两个大语言模型将相互对话")
        
        # Select first model
        print("\n选择第一个模型:")
        model1_name = self.choose_model()
        client1 = OllamaClient(model1_name)
        
        # Select second model
        print("\n选择第二个模型:")
        model2_name = self.choose_model()
        client2 = OllamaClient(model2_name)
        
        # Load both models
        print(f"\n正在载入模型: {model1_name} 和 {model2_name}")
        client1.load_model()
        client2.load_model()
        
        # Get conversation topic
        topic = input("\n请输入对话主题或初始提示: ")
        sys1 = topic + f"你是1号模型{model1_name} 你将与2号模型{model2_name}围绕{topic}进行对话,由1号模型（你）先说话，在说话的时候你应该表明自己的身份（1号ai）"
        sys2 = topic + f"你是2号模型{model2_name} 你将与1号模型{model1_name}围绕{topic}进行对话,你会在1号模型（其他ai模型）说完后说话，在说话的时候你应该表明自己的身份（2号ai）"
        print(f"\n对话主题: {topic}")
        
        
        # Initialize conversation histories for each model
        conversation1 = [{"role": "system", "content": sys1}]
        conversation1.append({"role": "user", "content": "你先说话"})
        conversation2 = [{"role": "system", "content": sys2}]
        
        print(f"\n=== 开始 {model1_name} 与 {model2_name} 的对话 ===")
        print(f"主题: {topic}\n")
        
        # Run conversation for specified number of exchanges
        i = 0
        while True:
            # First model responds
            i += 1
            if num_exchanges - i <= 0:
                print(f"已经进行了 {num_exchanges} 次对话,你希望继续吗？(y/n): ", end='')
                continue_choice = input()
                if continue_choice.lower() != 'y':
                    print("感谢使用，再见！")
                    break
                else:
                    print("你希望继续多少次对话？(默认5次): ", end='')
                    add = input()
                    num_exchanges = int(add) if add.isdigit() else 5
                    print(f"继续对话，当前对话次数: {i}/{num_exchanges}")


            print(f"[{model1_name}]: ", end='', flush=True)
            response1 = client1.stream_chat(conversation1)
            
            if not response1:
                print("\n对话中断: 第一个模型未能响应")
                break
            
            # Process think part for model 1
            think_part1, after_think_part1 = take_part_of_conversation(response1)
            
            # Update conversation histories
            conversation1.append({"role": "assistant", "content": response1})  # Model 1 sees its own think part
            conversation2.append({"role": "user", "content": after_think_part1 if think_part1 else response1})  # Model 2 only sees after_think part
            
            # Second model responds
            print(f"\n[{model2_name}]: ", end='', flush=True)
            response2 = client2.stream_chat(conversation2)
            
            if not response2:
                print("\n对话中断: 第二个模型未能响应")
                break
            
            # Process think part for model 2
            think_part2, after_think_part2 = take_part_of_conversation(response2)
                
            # Update conversation histories
            conversation2.append({"role": "assistant", "content": response2})  # Model 2 sees its own think part
            conversation1.append({"role": "user", "content": after_think_part2 if think_part2 else response2})  # Model 1 only sees after_think part
            
            print()  # Add spacing between exchanges
        
        print("\n=== 对话结束 ===")
        
        # Ask if user wants to save the conversation
        save = input("\n是否保存对话记录? (y/n): ")
        if save.lower() == 'y':
            filename = input("请输入文件名: ")
            with open(f"{filename}.txt", "w", encoding="utf-8") as f:
                f.write(f"对话主题: {topic}\n")
                f.write(f"模型 1: {model1_name}\n")
                f.write(f"模型 2: {model2_name}\n\n")
                
                # Write conversation
                for i in range(len(conversation1) // 2):
                    user_msg = conversation1[i*2]["content"]
                    model1_msg = conversation1[i*2+1]["content"]
                    model2_msg = conversation2[i*2+1]["content"] if i*2+1 < len(conversation2) else ""
                    
                    if i == 0:
                        f.write(f"初始提示: {user_msg}\n")
                    f.write(f"[{model1_name}]: {model1_msg}\n")
                    if model2_msg:
                        f.write(f"[{model2_name}]: {model2_msg}\n")
            
            print(f"对话已保存至 {filename}.txt")
            self.ifchat = False


def main():
    chat = ChatInterface()
    chat.run_chat_session()

def get_screenshot_info():
    """Get screenshot info using OllamaClient"""
    start_time = time.time()
    client = OllamaClient()
    client.model = "qwen2.5vl:7b"
    client.getscreenshotinfo()
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"获取屏幕截图信息完成，耗时: {elapsed_time:.2f} 秒")

if __name__ == "__main__":
    get_screenshot_info()
