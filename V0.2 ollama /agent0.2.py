#两个优化 增加错误优化和结束聊天优化
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
        print("建议检查模型型号是否正确")
        print(f"错误: {str(e)}")
        return None

def main():
    print("欢迎使用Ollama聊天机器人 (llama3:18b 模型)")
    print("输入 'quit' 或 'exit' 结束对话")
    is_cvsions_end = False
    conversation = []
    while True:
        user_input = input("\n您: ")
        if user_input.lower() in ['quit', 'exit', 'goodbye', 'bye', 'see you', 'later', 'farewell','再见', '拜拜', '下次见', '回头见', '走了', '告辞']:
            is_cvsions_end = True

        conversation.append({"role": "user", "content": user_input})
        print("\nAI: ", end='', flush=True)
        
        ai_response = stream_chat(conversation)
        if ai_response:
            conversation.append({"role": "assistant", "content": ai_response})
        if is_cvsions_end:
            break

if __name__ == "__main__":
    main()
