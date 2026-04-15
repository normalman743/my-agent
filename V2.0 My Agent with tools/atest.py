import openai
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

# OpenAI API的域名
openai_domain = 'api.openai.com'

print("Tracing route to OpenAI API:")
trace_route(openai_domain)

# 尝试一个简单的API调用
try:
    response = openai.Completion.create(engine="text-davinci-002", prompt="Hello, World!", max_tokens=5)
    print("\nAPI call successful")
except Exception as e:
    print(f"\nAPI call failed: {str(e)}")