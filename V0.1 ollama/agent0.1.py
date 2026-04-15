import requests
import json

OLLAMA_API_URL = "http://localhost:11434/api/chat"

def stream_chat(messages):
    payload = {
        "model": "llama3.1:8b",
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
        print(f"错误: {str(e)}")
        return None

def main():
    print("欢迎使用Ollama聊天机器人 (llama3:18b 模型)")
    print("输入 'quit' 或 'exit' 结束对话")

    conversation = []
    while True:
        user_input = input("\n您: ")
        if user_input.lower() in ['quit', 'exit']:
            print("谢谢使用，再见！")
            break

        conversation.append({"role": "user", "content": user_input})
        print("\nAI: ", end='', flush=True)
        
        ai_response = stream_chat(conversation)
        if ai_response:
            conversation.append({"role": "assistant", "content": ai_response})

if __name__ == "__main__":
    main()
