# -*- coding: utf-8 -*-
"""Runner script for Property Document OCR Web Server"""
import sys
import os
import subprocess

# 1. Force execution with local .venv python if available
repo_dir = os.path.dirname(os.path.abspath(__file__))
venv_python = os.path.join(repo_dir, ".venv", "Scripts", "python.exe")
if os.path.exists(venv_python) and os.path.normpath(sys.executable).lower() != os.path.normpath(venv_python).lower():
    print(f"[PlotChoice] Launching via local project environment: {venv_python}")
    sys.exit(subprocess.call([venv_python] + sys.argv))


def ensure_port_free(port=8000):
    """Release port 8000 if a previous or zombie process is holding it on Windows."""
    if sys.platform != "win32":
        return
    try:
        current_pid = os.getpid()
        cmd = f"netstat -ano"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if f":{port}" in line and ("LISTENING" in line or "BOUND" in line.upper() or "CLOSE_WAIT" in line):
                parts = line.strip().split()
                if parts:
                    pid_str = parts[-1]
                    try:
                        pid = int(pid_str)
                        if pid > 0 and pid != current_pid:
                            print(f"[PlotChoice] Freeing port {port} from previous process tree (PID {pid})...")
                            subprocess.run(f"taskkill /F /T /PID {pid}", shell=True, capture_output=True)
                    except ValueError:
                        pass
    except Exception as err:
        print(f"[PlotChoice] Port check warning: {err}")


def _launch_browser_when_ready(url="http://127.0.0.1:8000"):
    """Poll the health check endpoint and automatically open the default browser when live."""
    import time
    import urllib.request
    import webbrowser

    for _ in range(30):
        time.sleep(0.5)
        try:
            req = urllib.request.Request(f"{url}/api/health")
            with urllib.request.urlopen(req, timeout=1) as resp:
                if resp.status == 200:
                    print(f"\n[PlotChoice] >>> Server is ready! Automatically opening web browser to: {url} <<<\n")
                    webbrowser.open(url)
                    return
        except Exception:
            pass


if __name__ == "__main__":
    import threading

    ensure_port_free(8000)

    # Launch browser automatically once uvicorn finishes startup
    threading.Thread(target=_launch_browser_when_ready, daemon=True).start()

    import uvicorn
    print("=========================================================")
    print("  PlotChoice Real Estate OCR & Intelligence Server")
    print("  Web Application URL: http://127.0.0.1:8000")
    print("  Web browser will launch automatically in a moment...")
    print("  (Keep this terminal window running while using the app)")
    print("=========================================================")
    uvicorn.run("app.server:app", host="127.0.0.1", port=8000, reload=True, reload_dirs=["app", "static"], access_log=True)


