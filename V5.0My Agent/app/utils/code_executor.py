import os
from config.config import config

def execute_python(code, security_level=1):
    """执行Python代码并返回结果，支持不同的安全等级"""
    
    try:
        # 从config读取允许的库和API
        allowed_libraries = config.get('allowed_libraries', {})
        apis = config.get('apis', {})
        
        # 根据安全等级调整允许的库
        if security_level == 2:
            allowed_libraries = {}  # 安全等级 2 不允许任何库
        
        # 创建一个安全的执行环境
        exec_globals = {
            "__builtins__": {} if security_level == 2 else __builtins__,
            "print": lambda *args: exec_globals.setdefault('output', []).append(' '.join(map(str, args)))
        }
        
        # 根据安全等级添加允许的库
        if security_level >= 1:
            for lib in allowed_libraries:
                if lib == "requests":
                    import requests
                    exec_globals["requests"] = requests
                # 可以添加更多库的导入逻辑
        
        # 添加来自config的API
        if security_level >= 1 and apis:
            exec_globals.update(apis)
        
        # 执行代码
        exec(code, exec_globals)
        return '\n'.join(exec_globals.get('output', []))
    except Exception as e:
        return str(e)