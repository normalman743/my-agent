tools_config = {
    "gpt-4": ["code_executor", "search_engine"],
    "claude-v1": ["message_formatter", "token_counter"],
    "star-llama-3.1-8b": ["all_tools_available_for_star"],
    "default": ["default_tool"],
    "brain_gpt":["terminal"],
}


# tools.config.py

tools_details = {
    "terminal": {
        "type": "function",
        "function": {
            "name": "execute_terminal_command",
            "description": "Execute terminal commands and return the output",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The terminal command to execute"
                    }
                },
                "required": ["command"]
            }
        }
    },
    "code_executor": {
        "type": "function",
        "function": {
            "name": "execute_code",
            "description": "Execute Python code snippets",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The Python code to execute"
                    }
                },
                "required": ["code"]
            }
        }
    },
    "search_engine": {
        "type": "function",
        "function": {
            "name": "search_google",
            "description": "Search Google for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            }
        }
    }
    # 可以继续为其他工具添加详细结构
}


def get_tools_for_model(model_name):
    return tools_config.get(model_name, tools_config["default"])

def get_tool_details(tool_name):
    return tools_details.get(tool_name)