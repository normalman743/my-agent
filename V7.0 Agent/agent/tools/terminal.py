"""
Terminal tool — execute shell commands with safety controls.

Evolved from V6.0's execute_shell_command, now with:
- Automatic sudo confirmation flow
- Configurable timeout
- Dangerous command detection
"""
import shlex
import subprocess
import time
import logging

from agent.tools.registry import tool
from agent.config import settings

logger = logging.getLogger(__name__)

# Commands that require extra confirmation
_DANGEROUS_PATTERNS = [
    "rm -rf", "mkfs", "dd if=", "shutdown", "reboot",
    "systemctl stop", "kill -9", "> /dev/", "chmod 777",
    "DROP ", "DELETE FROM", "TRUNCATE",
]


def _is_dangerous(command: str) -> bool:
    cmd_lower = command.lower()
    return any(pattern.lower() in cmd_lower for pattern in _DANGEROUS_PATTERNS)


def _confirm_execution(command: str, reason: str = "sudo") -> bool:
    """Ask user for confirmation. Respects TRUST setting."""
    if settings.trust:
        print(f"  ⚡ Auto-approved ({reason}): {command}")
        time.sleep(1)
        return True

    print(f"\n  ⚠️  Confirmation required ({reason})")
    print(f"  Command: {command}")
    answer = input("  Execute? [y/N]: ").strip().lower()
    return answer == "y"


@tool(description="Execute a shell command on the local system. Use sudo=true for privileged operations. Set timeout in seconds.")
def terminal(command: str, sudo: bool = False, timeout: int = 60) -> str:
    """Execute a shell command and return its output."""
    if not command or not command.strip():
        return "Error: empty command"

    # Build final command
    cmd = f"sudo {command}" if sudo else command

    # Safety checks
    if _is_dangerous(cmd):
        if not _confirm_execution(cmd, reason="dangerous command"):
            return "Cancelled by user"

    elif sudo:
        if not _confirm_execution(cmd, reason="sudo"):
            return "Cancelled by user"

    logger.info("Executing: %s", cmd)

    try:
        process = subprocess.run(
            shlex.split(cmd),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = process.stdout if process.returncode == 0 else process.stderr
        if not output.strip():
            output = f"(exit code: {process.returncode})"
        return output
    except subprocess.TimeoutExpired:
        return f"Error: command timed out after {timeout}s"
    except FileNotFoundError:
        return f"Error: command not found — {shlex.split(cmd)[0]}"
    except Exception as e:
        return f"Error: {e}"
