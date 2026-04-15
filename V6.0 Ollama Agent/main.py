#两个优化 增加错误优化和结束聊天优化
import requests
import json
from config import Config
from chat import stream_chat, tools_chat, json_chat

config = Config()
OLLAMA_API_URL = config.OLLAMA_API_URL
model = config.MODEL
tools = config.TOOLS
debug = config.DEBUG
system_prompt = config.SYSTEM_PROMPT

def load_model(load):
    if not isinstance(load, bool):
        print("请检查是否正确输入True或False")
        return None
    if load:
        print(f"正在加载 {model} 模型")
    else:
        print(f"正在卸载 {model} 模型")

    payload = {
        "model": model,
        "messages": [],
        "keep_alive": 0 if not load else "5m"
    }
    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        if not load:
            print(f" {model} 已卸载memory")
        else:
            print(f" {model} 已成功加载")
        return response.json()

    except requests.exceptions.RequestException as e:
        print("加载模型时出错，请检查API是否正确")
        print(f"错误: {str(e)}")
        exit(1)

def main():
    print(f"欢迎使用Ollama聊天机器人 ({model} 模型)")   
 
    load_model(True)
    print("输入 'quit' 或 'exit' 结束对话")
    is_cvsions_end = False
    conversation = [{"role": "system", "content": config.SYSTEM_PROMPT}]
    while True:
        if debug:
            user_input = "你好"
        else:
            user_input = input("\nSteven: ")

        if user_input.lower() in ['quit', 'exit', 'goodbye', 'bye', 'see you', 'later', 'farewell','再见', '拜拜', '下次见', '回头见', '走了', '告辞']:
            is_cvsions_end = True

        conversation.append({"role": "user", "content": user_input})

        print("\nStar: ", end='', flush=True)
        ai_response = tools_chat(conversation)

        if ai_response:
            conversation.append({"role": "assistant", "content": ai_response})
        if is_cvsions_end:
            break

if __name__ == "__main__":
    main()
    load_model(False)
