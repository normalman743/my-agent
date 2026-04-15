from openai import OpenAI
import requests
import socket
import os
# 设置你的OpenAI API密钥
os.environ.setdefault("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))


def get_ip_address(domain):
    try:
        return socket.gethostbyname(domain)
    except socket.gaierror:
        return None

def trace_route(domain):
    ip = get_ip_address(domain)
    if ip:
        print(f"Domain: {domain}")
        print(f"IP Address: {ip}")
        
        # 使用ipinfo.io API获取IP地址的地理位置信息
        response = requests.get(f'https://ipinfo.io/{ip}/json')
        if response.status_code == 200:
            data = response.json()
            print(f"Location: {data.get('city', 'N/A')}, {data.get('region', 'N/A')}, {data.get('country', 'N/A')}")
            print(f"ISP: {data.get('org', 'N/A')}")
    else:
        print(f"Could not resolve IP for {domain}")

client = OpenAI()
def chat_with_ai(messages, temperature=1, max_tokens=256, top_p=1, frequency_penalty=0, presence_penalty=0):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "execute_command",
                    "description": "Execute a block of terminal code and return the result.(mac)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "The terminal code to be executed."
                            }
                        },
                        "required": [
                            "code"
                        ],
                        "additionalProperties": False
                    },
                    "strict": False
                }
            },
        ],
        response_format={
            "type": "text"
        }
    )
    return response



# OpenAI API的域名
openai_domain = 'api.openai.com'

print("Tracing route to OpenAI API:")
trace_route(openai_domain)
conversation_history = []
conversation_history.append({"role": "user", "content": "hi"})
# 尝试一个简单的API调用
try:
    response = chat_with_ai(conversation_history)
    print("\nAPI call successful")
except Exception as e:
    print(f"\nAPI call failed: {str(e)}")