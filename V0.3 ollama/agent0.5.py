#两个优化 增加错误优化和结束聊天优化
import requests
import json
OLLAMA_API_TAGS_URL = "http://localhost:11434/api/tags"
OLLAMA_API_URL = "http://localhost:11434/api/chat"

def stream_chat(messages,model):
    payload = {
        "model": model,
        "messages": messages,
        "stream": True
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload, stream=True)
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
                    print()  # 换行
                    break

        return full_response.strip()

    except requests.exceptions.RequestException as e:
        print("建议检查模型型号是否正确，或ollama是否打开")
        print(f"错误: {str(e)}")
        return None

def main(model="llama3.1:8b"):
    print()
    print()
    print("欢迎使用 Ollama 聊天助手")
    print(f"正在载入模型: {model}")
    print("请稍等...")
    load_model = requests.post(OLLAMA_API_URL, json={"model": model})
    print("输入 'quit' 或 'exit' 结束对话")
    is_cvsions_end = False
    conversation = []
    while True:
        user_input = input("\n您: ")
        if user_input.lower() in ['quit', 'exit', 'goodbye', 'bye', 'see you', 'later', 'farewell','再见', '拜拜', '下次见', '回头见', '走了', '告辞']:
            is_cvsions_end = True

        conversation.append({"role": "user", "content": user_input})
        print("\nAI: ", end='', flush=True)
        
        ai_response = stream_chat(conversation,model)
        if ai_response:
            conversation.append({"role": "assistant", "content": ai_response})
        if is_cvsions_end:
            break
def choose_model():
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
        if category_choice == '2':
            return "llama3.1:8b"
        if category_choice == '4':
            return "phi4:latest"
        
        if category_choice == '3':
            response = requests.get(OLLAMA_API_TAGS_URL)
            models_data = response.json()
            models_list = models_data['models']
            print("可用模型列表:")
            for i, model in enumerate(models_list):
                print(f"{i + 1}. {model['name']} - {model['details']['parameter_size']}")
                j = i+1
            print(f"{j + 1}. 退出")
            choose_model_num = int(input("请输入模型编号: "))
            if 1 <= choose_model_num <= len(models_list):
                model = models_list[choose_model_num - 1]
                print(f"您选择的模型是: {models_list[choose_model_num - 1]['name']}")
                # 确认模型/获得更多信息
                print("模型信息:")
                print(f"名称: {models_list[choose_model_num - 1]['name']}")
                print(f"模型大小: {models_list[choose_model_num - 1]['details']['parameter_size']}")
                if model['name'] == 'snowflake-arctic-embed2:latest':
                        print("该模型为嵌入模型，无法使用对话")
                        print("该模型为嵌入模型，无法使用对话")
                        print("该模型为嵌入模型，无法使用对话")
                more_info = input("是否需要更多信息？(y/n): ")
                if more_info.lower() == 'y':
                    details = model["details"]
                    print(f"模型修改时间: {models_list[choose_model_num - 1]['modified_at']}")
                    print(f"模型标签: {models_list[choose_model_num - 1]['digest']}")
                    for key, value in details.items():
                        print(f"  - {key}: {value}")
                confrim = input("是否确认使用该模型？(y/n): ")
                if confrim.lower() == 'y':
                    return models_list[choose_model_num - 1]['name']
                else:
                    print("请重新选择模型")
                    continue
            elif choose_model_num == len(models_list) + 1:
                print("感谢使用，再见！")
                break
            else:
                print("无效选择，请重试")
                continue

        if category_choice == '5':
            print("感谢使用，再见！")
            break
        else:
            print("无效选择，请重试")
            continue
    return "qwen3:latest"

if __name__ == "__main__":
    main(choose_model())
