import subprocess

def check_ollama(port=11434, modelname='llama3.1:8b'):
    try:
        # 使用 lsof 命令检查端口
        result = subprocess.check_output(['lsof', '-i', f':{port}'], text=True, stderr=subprocess.STDOUT)
        
        if result.strip():
            # 解析 lsof 命令的输出，检查是否有进程占用端口
            lines = result.strip().split('\n')
            if any('ollama' in line.lower() for line in lines):
                print(f"ollama已经启用")
            else:
                print(f"端口 {port} 被其他进程占用。")
                user_input = input("端口被抢占，是否停止该进程并运行 Ollama？（Y/N）：").strip().upper()
                if user_input == 'Y':
                    pid = int(lines[1].split()[1])  # 获取进程 ID（假设占用端口的进程是第一行）
                    subprocess.run(['kill', str(pid)], check=True)
                    print(f"已停止进程 {pid}。")
    except subprocess.CalledProcessError as e:
        if e.output:
            print(f"命令执行失败: {e.cmd}")
            print(f"错误代码: {e.returncode}")
            print(f"错误输出: {e.output.decode() if e.output else '无输出'}")
        else:
            try:
                print("正在启动Ollama 服务。")
                process = subprocess.Popen(['/usr/local/bin/ollama', 'serve'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                print("Ollama 服务已启动。")
                try:
                    subprocess.run(['/usr/local/bin/ollama', 'run','example'], check=True)
                except:
                    print("ollama serve not work ,we try ollama run example hope that work")
            except subprocess.CalledProcessError as e:
                print(f"运行ollama时发生一个错误:{e}")

# 示例调用
if __name__ == "__main__":
    port = 11434
    modelname = "your_model_name_here"
    check_ollama(port, modelname)
