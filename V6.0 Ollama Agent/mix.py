from config import Config
import requests
import json
import subprocess
import shlex
import time
import paramiko
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SSHConnection:
    def __init__(self, hostname, username, key_filename, port=22):
        self.hostname = hostname
        self.username = username
        self.key_filename = key_filename
        self.port = port
        self.ssh = None

    def connect(self):
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(
                hostname=self.hostname,
                username=self.username,
                key_filename=self.key_filename,
                port=self.port
            )
            return True
        except Exception as e:
            logger.error(f"SSH connection failed: {e}")
            return False

    def execute_command(self, command):
        if not self.ssh:
            return "SSH connection not established"
        try:
            stdin, stdout, stderr = self.ssh.exec_command(command)
            output = stdout.read().decode()
            error = stderr.read().decode()
            return error if error else output
        except Exception as e:
            return f"Command execution failed: {e}"

    def close(self):
        if self.ssh:
            self.ssh.close()
            self.ssh = None

def execute_shell_command(tool_calls, ssh_connection=None):
    if not tool_calls:
        return "No command provided"
    
    command = tool_calls[0].get('function', {}).get('arguments', {}).get('command', None)
    use_ssh = tool_calls[0].get('function', {}).get('arguments', {}).get('use_ssh', False)
    sudo = tool_calls[0].get('function', {}).get('arguments', {}).get('sudo', False)
    timeout = tool_calls[0].get('function', {}).get('arguments', {}).get('timeout', 10)

    if command is None:
        return "No command provided"

    if sudo:
        command = f"sudo {command}"

    if use_ssh and ssh_connection:
        return ssh_connection.execute_command(command)
    else:
        try:
            process = subprocess.run(
                shlex.split(command),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return process.stdout if process.returncode == 0 else process.stderr
        except Exception as e:
            return str(e)

def tools_chat(messages, ssh_connection=None):
    config = Config()
    payload = {
        "model": config.MODEL,
        "messages": messages,
        "stream": False,
        "tools": json.loads(config.TOOLS).get('tools')
    }

    try:
        response = requests.post(config.OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        message = response.json().get('message', {})
        tool_calls = message.get('tool_calls', '')
        
        if tool_calls:
            messages.append(message)
            tools_result = execute_shell_command(tool_calls, ssh_connection)
            messages.append({"role": "tool", "content": tools_result, "name": "execute_shell_command"})
            return tools_chat(messages, ssh_connection)
        else:
            return message.get('content', '')

    except requests.exceptions.RequestException as e:
        print("建议检查模型型号是否正确，或ollama是否打开")
        print(f"错误: {str(e)}")
        exit(1)

def main():
    config = Config()
    print(f"Welcome to Ollama Chat Bot ({config.MODEL} model)")
    
    # SSH Configuration — load from environment
    ssh_connection = SSHConnection(
        hostname=os.getenv("SSH_HOST", ""),
        username=os.getenv("SSH_USER", "root"),
        key_filename=os.getenv("SSH_KEY_PATH", ""),
        port=int(os.getenv("SSH_PORT", "22"))
    )
    
    if ssh_connection.connect():
        print("SSH connection established")
    else:
        print("Failed to establish SSH connection")
        return

    conversation = [{"role": "system", "content": config.SYSTEM_PROMPT}]
    
    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() in ['quit', 'exit', 'bye', '再见', '拜拜']:
            break

        conversation.append({"role": "user", "content": user_input})
        print("\nAI: ", end='', flush=True)
        
        ai_response = tools_chat(conversation, ssh_connection)
        if ai_response:
            conversation.append({"role": "assistant", "content": ai_response})

    ssh_connection.close()
    print("Session ended")

if __name__ == "__main__":
    main()