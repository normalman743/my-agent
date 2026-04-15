"""
SSH tool — execute commands on remote machines.

Requires SSH_HOST, SSH_USER, SSH_KEY_PATH in .env.
Uses paramiko for key-based authentication.
"""
import logging

from agent.tools.registry import tool
from agent.config import settings

logger = logging.getLogger(__name__)

# Lazy-loaded SSH connection
_ssh_client = None


def _get_ssh():
    """Lazy init SSH connection. Returns paramiko.SSHClient or None."""
    global _ssh_client
    if _ssh_client is not None:
        return _ssh_client

    if not settings.ssh.enabled:
        return None

    try:
        import paramiko
    except ImportError:
        logger.warning("paramiko not installed — SSH tool disabled")
        return None

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=settings.ssh.host,
            port=settings.ssh.port,
            username=settings.ssh.user,
            key_filename=settings.ssh.key_path or None,
        )
        _ssh_client = client
        logger.info("SSH connected to %s@%s", settings.ssh.user, settings.ssh.host)
        return _ssh_client
    except Exception as e:
        logger.error("SSH connection failed: %s", e)
        return None


def close_ssh():
    """Clean up SSH connection."""
    global _ssh_client
    if _ssh_client:
        _ssh_client.close()
        _ssh_client = None
        logger.info("SSH connection closed")


@tool(description="Execute a command on the configured remote server via SSH. Requires SSH settings in .env.")
def ssh_exec(command: str, timeout: int = 30) -> str:
    """Execute a command over SSH and return the output."""
    ssh = _get_ssh()
    if ssh is None:
        return "Error: SSH not configured or connection failed. Set SSH_HOST, SSH_USER in .env."

    try:
        _, stdout, stderr = ssh.exec_command(command, timeout=timeout)
        output = stdout.read().decode()
        error = stderr.read().decode()
        return error if error and not output else output
    except Exception as e:
        return f"SSH execution error: {e}"
