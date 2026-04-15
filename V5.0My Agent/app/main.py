from app.utils.code_executor import execute_python
from app.utils.llm_client import get_llm_client
from app.utils.message_formatter import format_message , format_ai_message
from app.utils.search_engine import SearchEngine
from app.utils.token_counter import count_tokens
import config, json
from config.promote import BRAIN_PROMPT
from config.hint import HINTS
import re

def convert_multiline_to_json_compatible(data):
    """
    递归遍历字典，将其中的多行字符串转换为符合 JSON 规范的单行字符串
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str):
                # 如果字符串包含换行符，将其替换为 \n
                data[key] = value.replace('\n', '\\n')
            elif isinstance(value, dict):
                # 如果值本身是字典，递归调用
                convert_multiline_to_json_compatible(value)
    return data

def chat(user_input, conversation, client):
    formatted_input = format_message("Steven", user_input, HINTS["user_input"])
    
    # 将 JSON 字符串解析为字典
    formatted_input_dict = json.loads(formatted_input)
    conversation.append({"role": "user", "content": formatted_input})
    
    # 使用 chat_with_llm 来获取流式响应
    status, full_response = client.chat_with_llm(conversation)
    print(full_response)

def respond(python_respond, conversation, client):
    formatted_input = format_message("python", python_respond, HINTS["python_result"])
    
    # 将 JSON 字符串解析为字典
    formatted_input_dict = json.loads(formatted_input)
    conversation.append({"role": "user", "content": formatted_input})
    
    # 使用 chat_with_llm 来获取流式响应
    status, full_response = client.chat_with_llm(conversation)
    
    # 根据流式响应的完整性和格式处理返回结果
    try:
        ai_response = json.loads(full_response)
        status = ai_response.get("status", "reply")
        message = ai_response.get("message", full_response)
    except json.JSONDecodeError:
        status = "reply"
        message = full_response

    if status == "python":
        result = execute_python(message)
        conversation.append({"role": "user", "content": format_message("python", result, HINTS["python_result"])})
        return "python", message, result
    elif status == "reply":
        return "reply", message, None
    else:
        return "error", "未知状态", None

def main():
    # Load the LLM client
    client = get_llm_client("openai")
    
    conversation = []  # 初始化对话记录
    default_prompt = BRAIN_PROMPT  # 从配置文件中获取默认提示文本
    conversation.append({"role": "system", "content": default_prompt})  # 添加系统提示

    print("欢迎使用AI助手Star。输入 'quit' 或 'exit' 结束对话。")
    
    debug = False  # 是否启用调试模式
    while True:
        if debug:
            try:
                print(f"result is {result}")
                print(f"conversation is {conversation}")
                print(f"status is {status}")
                print(f"message is {message}")
            except:
                pass

        user_input = input("\n请输入您的问题: ")  # 获取用户输入
            
        if user_input.lower() in ['quit', 'exit']:  # 检查退出条件
            print("感谢使用，再见！")
            break
        
        status, message, result = chat(user_input, conversation,client)  # 调用 chat 函数
        
        json_string_escaped = re.sub(r'""".*?"""', lambda m: '"' + m.group(0).replace('\n', '\\n').replace('"', '\\"') + '"', message, flags=re.DOTALL)
        # 解析 JSON 字符串
        try:
            message_dict = json.loads(json_string_escaped)
            message = message_dict["Message"]
        except json.JSONDecodeError as e:
            print("JSONDecodeError:", e)
            
        print(f"status is {status}")
        if status == "python":
            result = execute_python(message)
            if debug:
                print("\nAI生成的Python代码:")
                print(message)
                print("\n执行结果:")
                print(result)
        elif status == "reply":
            if debug:
                print("\nAI回复:")
                print(message)
        else:
            print("\n发生错误:")
            print(message)
            break

if __name__ == '__main__':
    main()