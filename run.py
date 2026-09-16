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


if __name__ == "__main__":
    ensure_port_free(8000)
    import uvicorn
    print("=========================================================")
    print("  Starting Real Estate Document OCR & Intelligence Server")
    print("  Access Web Application at: http://127.0.0.1:8000")
    print("=========================================================")
    uvicorn.run("app.server:app", host="127.0.0.1", port=8000, reload=True, reload_dirs=["app", "static"], access_log=True)


