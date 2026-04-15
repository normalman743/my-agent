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

def ssh_connect(hostname, username, key_filename, port=22):
    try:
        # Create SSH client
        ssh = paramiko.SSHClient()
        
        # Automatically add the server's host key
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect to the server
        ssh.connect(
            hostname=hostname, 
            username=username, 
            key_filename=key_filename, 
            port=port
        )
        
        # Execute a command
        stdin, stdout, stderr = ssh.exec_command('ls -l')
        
        # Print command output
        print(stdout.read().decode())
        
        # Print any error output
        error = stderr.read().decode()
        if error:
            print(f"Error: {error}")
        
        return ssh
    
    except paramiko.AuthenticationException:
        logger.error("Authentication failed")
    except paramiko.SSHException as ssh_exception:
        logger.error(f"SSH connection failed: {ssh_exception}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

def getcommand():
    command = input("Enter command: ")
    return command

def setupssh():
    # Configuration — load from environment
    hostname = os.getenv("SSH_HOST", "")
    port = int(os.getenv("SSH_PORT", "22"))
    username = os.getenv("SSH_USER", "root")
    key_filename = os.getenv("SSH_KEY_PATH", "")
    
    # Establish SSH connection
    ssh = ssh_connect(hostname, username, key_filename, port)
    
    # Close the connection if it was successful
    if ssh:
        while True:
            try:
                # Execute a command
                command = getcommand()
                if command.lower() in ['q', 'quit', 'exit']:
                    break
                stdin, stdout, stderr = ssh.exec_command(command)
                print(stdout.read().decode())
                
                # Check for errors
                error = stderr.read().decode()
                if error:
                    print(f"Error: {error}")
            except Exception as e:
                logger.error(f"Connection error: {e}")
                break
    else:
        logger.error("Failed to establish SSH connection")
            
    ssh.close()
    logger.info("SSH connection closed")

    
config = Config()

model = config.MODEL
OLLAMA_API_URL = config.OLLAMA_API_URL
tools_json_str = config.TOOLS
tools = json.loads(tools_json_str).get('tools')
System_prompt = config.SYSTEM_PROMPT
trust = config.TRUST

def execute_shell_command(tool_calls):
    # EG：[{'function': {'name': 'execute_shell_command', 'arguments': {'command': 'ls'}}}]
    if not tool_calls:
        return "No command provided"
    elif len(tool_calls) > 1:
        return "Please provide only one command at a time"
    command = tool_calls[0].get('function', {}).get('arguments', {}).get('command', None)
    sudo = False if tool_calls[0].get('function', {}).get('arguments', {}).get('sudo', False) == 'false' else True
    timeout = int(tool_calls[0].get('function', {}).get('arguments', {}).get('timeout', 10))

    
    if command is None:
        return "No command provided"
    if sudo:
        cmd = f"sudo {command}"
        print(f"The ai wanna execute: {cmd}")
        print(f"Please confirm if you want to execute this command")    
        if trust == "True":
            print("The command will be executed within 3 seconds")
            time.sleep(3)
        else:
            command_confirm = input("Please confirm if you want to execute this command (y/n): ")
            if command_confirm.lower() != 'y':
                return "Command execution cancelled by user"
    else:
        cmd = command

    try:
        process = subprocess.run(
            shlex.split(cmd),
            capture_output=True,
            text=True,
            timeout=timeout
        )
        print(f"Command executed: {cmd}")
        print(f"Result: {process.stdout}")
        return process.stdout if process.returncode == 0 else process.stderr
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout} seconds"
    except Exception as e:
        return str(e)
    
def tools_chat(messages):
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "tools": tools
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        message = response.json().get('message', {})
        tool_calls = response.json().get('message', {}).get('tool_calls', '')
        
        if tool_calls:
            #havprint(tool_calls[0].get('function', {}).get('arguments', {}).get('command', None))
            messages.append(message)
            tools_result = execute_shell_command(tool_calls)
            messages.append({"role": "tool", "content": tools_result , "name": "execute_shell_command"})
            return tools_chat(messages)
        else:
            print(message.get('content', ''))
            return message.get('content', '')

    except requests.exceptions.RequestException as e:
        print("建议检查模型型号是否正确，或ollama是否打开")
        print(f"错误: {str(e)}")
        exit(1)


def json_chat(messages):
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "format": "json"
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print("建议检查模型型号是否正确，或ollama是否打开")
        print(f"错误: {str(e)}")
        exit(1)

def stream_chat(messages):
    payload = {
        "model": model,
        "messages": messages,
        "stream": True
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload, stream=True)
        response.raise_for_status()

        full_response = ""
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line)
                if 'message' in chunk:
                    content = chunk['message'].get('content', '')
                    full_response += content
                    print(content, end='', flush=True)
                if chunk.get('done', False):
                    print()  # 换行
                    break

        return full_response.strip()

    except requests.exceptions.RequestException as e:
        print("建议检查模型型号是否正确，或ollama是否打开")
        print(f"错误: {str(e)}")
        return None
