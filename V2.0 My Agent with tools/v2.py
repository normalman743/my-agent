from openai import OpenAI
import openai
import requests
import json

# 配置 OpenAI API 密钥
import os
Google_Search_API = os.getenv('GOOGLE_SEARCH_API_KEY', ''),
SCE_ID = os.getenv('GOOGLE_CSE_ID', '')

DEFAULT_PROMPT = """

你是一个名为Star的AI助手，作为Steven的个人AI帮手。

在每次交互中，你将接收文本形式的输入。你的任务是处理这个输入，并根据给定的信息做出适当的回应。

可用工具:

1. Python执行器：用于执行Python代码。

2. Google搜索：用于获取最新信息或补充知识。

你的回应应始终采用以下JSON格式:

{

    "think": "对用户意图的理解",

    "action": "你决定怎么完成用户的要求",

    "think_twice":"(可选）如果你不确定那么你可以再思考一次"

    "message": "你的回复内容",

    "reflection": "（可选）对这次交互的反思或自我评估"

}

指导原则:

1. 始终以友好、专业的态度回应。

2. 如果不确定用户的意图，请寻求澄清。

3. 使用Python来完成和用户电脑有关的任务。

4. 如果需要最新信息或补充知识，使用Google搜索。

6. 如果任务无法完成，请在"message"中解释原因。

7. 保持回答简洁明了，但必要时可以提供详细解释。

8. 如果用户要求执行危险或不道德的操作，礼貌地拒绝并解释原因。

9. 在"reflection"字段中，你可以添加对这次交互的思考、自我评估或改进建议。这是可选的，但可以帮助提高回答质量。

请记住，你是一个AI助手，应该在道德和安全的界限内提供帮助，同时利用所有可用工具来最大程度地满足用户需求。

"""
# Initialize the OpenAI client
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
                    "name": "execute_python",
                    "description": "Execute a block of Python code and return the result.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "The Python code to be executed."
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
            {
                "type": "function",
                "function": {
                    "name": "search_google",
                    "description": "Perform a Google search and return the results.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query to be executed."
                            }
                        },
                        "required": [
                            "query"
                        ],
                        "additionalProperties": False
                    },
                    "strict": False
                }
            }
        ],
        response_format={
            "type": "text"
        }
    )
    return response

def search_google(query):
    """Perform a Google search and return the results."""
    try:
        url = 'https://www.googleapis.com/customsearch/v1'
        params = {
            'key': Google_Search_API,
            'cx': SCE_ID,
            'q': query
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        search_results = response.json()
        results = []
        for item in search_results.get('items', []):
            title = item.get('title')
            link = item.get('link')
            results.append(f"Title: {title}, Link: {link}")
        return "\n".join(results) if results else "No results found."
    except Exception as e:
        return str(e)

def execute_python(code):
    """Execute a block of Python code and return the result."""
    try:
        local_vars = {}
        exec(code, globals(), local_vars)
        result = "\n".join(f"{k}: {v}" for k, v in local_vars.items())
        return result if result else "No result from code execution."
    except Exception as e:
        return str(e)
    
def execute_tool_call(tool_call):
    function = tool_call.function
    function_name = function.name
    arguments = json.loads(function.arguments)
    
    result = None
    if function_name == 'execute_python':
        code = arguments.get('code')
        if code:
            result = json.dumps({"code" : execute_python(code)})
        else:
            result = "No code provided for execution."
    
    elif function_name == 'search_google':
        query = arguments.get('query')
        if query:
            result = json.dumps({"query" : search_google(query)})
        else:
            result = "No query provided for search."
    
    else:
        result = "Unknown function or error."

    return result

def main():
    conversation_history = []
    conversation_history.append({"role": "system", "content": DEFAULT_PROMPT})
    
    while True:
        user_input = input("You: ")
        conversation_history.append({"role": "user", "content": user_input})
        
        # Fetch chat response
        chat_response = chat_with_ai(conversation_history)
        
        # Extract response content
        response = chat_response.choices[0].message.content
        
        # Extract tool results, if any
        tool_results = chat_response.choices[0].message.tool_calls if chat_response.choices[0].message.tool_calls else []

        if response:
            conversation_history.append({"role": "assistant", "content": response})
            print("Assistant:", response)
        

if __name__ == "__main__":
    main()
