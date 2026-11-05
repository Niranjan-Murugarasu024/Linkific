import os
from pathlib import Path
from src.utils.logger import get_logger
log=get_logger("sftp")

def collect_sftp():
    # Optional demonstration. Credentials are read from .env and never hard-coded.
    host=os.getenv("SFTP_HOST"); user=os.getenv("SFTP_USERNAME")
    remote=os.getenv("SFTP_REMOTE_PATH")
    if not all([host,user,remote]):
        log.info("SFTP not configured; skipped (set SFTP_* variables to enable)")
        return None
    import paramiko
    port=int(os.getenv("SFTP_PORT","22"))
    transport=paramiko.Transport((host,port))
    try:
        transport.connect(username=user,password=os.getenv("SFTP_PASSWORD"))
        sftp=paramiko.SFTPClient.from_transport(transport)
        local=Path("data/raw")/Path(remote).name
        sftp.get(remote,str(local))
        log.info("Downloaded SFTP file to %s",local)
        return str(local)
    finally:
        transport.close()
