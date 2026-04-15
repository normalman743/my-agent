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