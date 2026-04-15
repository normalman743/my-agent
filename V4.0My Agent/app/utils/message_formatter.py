import json

def format_message(role, message, hint=""):
    """格式化消息为新的JSON格式"""
    inner_content = {
        "role": role,
        "message": message,
        "hint": hint
    }
    inner_content = {k: v for k, v in inner_content.items() if v}
    print(inner_content)
    return json.dumps(inner_content, ensure_ascii=False)


def format_ai_message(think, status, message):
    """格式化消息为新的JSON格式"""
    inner_content = {
        "think": think,
        "status": status,
        "message": message
    }
    inner_content = {k: v for k, v in inner_content.items() if v}
    print(inner_content)
    return json.dumps(inner_content, ensure_ascii=False)


