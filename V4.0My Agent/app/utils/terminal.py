import subprocess
import time

def execute_command(command, mode="test"):
    if mode == "test":
        print(f"你即将执行的程序是：{command}")
        print("该程序将在10s后自动执行")
        print("使用control+c停止")
        
        for i in range(10, 0, -1):
            time.sleep(1)
            if i <= 3:
                print(f"程序将在{i}s后执行")
    
    try:
        # 执行命令
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        # 如果没有异常，返回 status 和 message
        return {
            'status': 'result',
            'message': result.stdout
        }
    except subprocess.CalledProcessError as e:
        # 如果发生异常，返回 status 和 message
        return {
            'status': 'error',
            'message': e.stderr
        }