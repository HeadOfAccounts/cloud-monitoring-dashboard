import os, socket, time
from datetime import datetime, timezone
import psutil, requests

API = os.environ.get("API_URL", "http://localhost:5000")
VM_ID = os.environ.get("VM_ID", socket.gethostname())
INTERVAL = int(os.environ.get("INTERVAL", 15))

def sample():
    return {
        "vm_id": VM_ID,
        "cpu": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage("/").percent,
        "uptime": int(time.time() - psutil.boot_time()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

while True:
    try:
        r = requests.post(f"{API}/metrics", json=sample(), timeout=5)
        print(r.status_code, r.text.strip())
    except requests.RequestException as e:
        print("send failed, will retry:", e)
    time.sleep(INTERVAL)