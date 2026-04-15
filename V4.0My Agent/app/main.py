from app.utils.code_executor import execute_python
from app.utils.llm_client import get_llm_client
from app.utils.message_formatter import format_message , format_ai_message
from app.utils.search_engine import SearchEngine
from app.utils.token_counter import count_tokens
import config, json
from config.promote import BRAIN_PROMPT
from config.hint import HINTS
import re
from app.utils.terminal import execute_command

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

def respond(python_respond, conversation, client):
    formatted_input = format_message("python", python_respond, HINTS["python_result"])
    
    conversation.append({"role": "user", "content": formatted_input})
    
    # 使用 chat_with_llm 来获取流式响应
    full_response = client.chat_with_llm(conversation)
    
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
    


def get_tool_response(conversation, client):
    full_response = ""
    for response_chunk in client.chat_with_llm(conversation):
        print(response_chunk, end='', flush=True)
        full_response += response_chunk




def chat(user_input, conversation, client,from_tool=False):
    if from_tool == False:
        formatted_input = format_message("Steven", user_input, HINTS["user_input"])
        conversation.append({"role": "user", "content": formatted_input})
    else:
        formatted_input = format_message("terminal", user_input, HINTS["user_input"])
        conversation.append({"role": "user", "content": user_input})



    # 使用 chat_with_llm 来获取流式响应
    full_response = ""
    for response_chunk in client.chat_with_llm(conversation):
        print(response_chunk, end='', flush=True)
        full_response += response_chunk
    
    print()  # 换行
    conversation.append({"role": "assistant", "content": full_response})

    if full_response.startswith('<|python_tag|>'):
        try:

            json_content = full_response[len('<|python_tag|>'):].strip()
            tool_message = json.loads(json_content)
        except json.JSONDecodeError:
            return "JSON Decode Error: Invalid JSON format"
        tool_name = tool_message.get("name")
        tool_params = tool_message.get("parameters", {})
        code = tool_params.get("code", "")
        execution_authority = tool_params.get("execution_authority", 1)

        if execution_authority != "general":
            result = "你没有权限执行此操作。"
        else:
            code_result = execute_command(code)
            result = {"output": code_result}
        chat(result, conversation, client,from_tool=True)


    return full_response

def main():
    # Load the LLM client
    client = get_llm_client("ollama")
    
    conversation = []  # 初始化对话记录
    default_prompt = BRAIN_PROMPT  # 从配置文件中获取默认提示文本
    conversation.append({"role": "system", "content": default_prompt})  # 添加系统提示

    print("欢迎使用AI助手Star。输入 'quit' 或 'exit' 结束对话。")
    
    debug = False  # 是否启用调试模式
    while True:
        if debug:
            try:
                print(f"conversation is {conversation}")
                print(f"message is {message}")
            except:
                pass

        user_input = input("\n请输入您的问题: ")  # 获取用户输入
            
        if user_input.lower() in ['quit', 'exit']:  # 检查退出条件
            print("感谢使用，再见！")
            break
        
        message = chat(user_input, conversation,client)  # 调用 chat 函数

if __name__ == '__main__':
    main()