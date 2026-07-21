import os
from dataclasses import dataclass

import paramiko


@dataclass
class SSHConfig:
    host: str
    user: str = "root"
    key_path: str = "~/.ssh/netscanner_pfsense"
    port: int = 22
    timeout: float = 10.0


def fetch_file(cfg: SSHConfig, remote_path: str, optional: bool = False) -> str | None:
    """Fetch a remote text file's contents over SSH using the trusted key.

    Host keys are verified against the user's existing known_hosts (populated
    when they first SSH'd in manually) rather than trusted on first use.

    If `optional` is set, a missing/unreadable file returns None instead of raising
    (connection-level failures still raise either way).
    """
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect(
        hostname=cfg.host,
        port=cfg.port,
        username=cfg.user,
        key_filename=os.path.expanduser(cfg.key_path),
        look_for_keys=False,
        allow_agent=False,
        timeout=cfg.timeout,
    )
    try:
        stdin, stdout, stderr = client.exec_command(f"cat -- {_quote(remote_path)}", timeout=cfg.timeout)
        data = stdout.read().decode("utf-8", errors="replace")
        exit_status = stdout.channel.recv_exit_status()
        if exit_status != 0:
            if optional:
                return None
            err = stderr.read().decode("utf-8", errors="replace").strip()
            raise RuntimeError(f"failed to read {remote_path!r} on {cfg.host}: {err or f'exit status {exit_status}'}")
        return data
    finally:
        client.close()


def _quote(path: str) -> str:
    return "'" + path.replace("'", "'\\''") + "'"
