import subprocess
import sys
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

def run_backend():
    return subprocess.Popen(
        [sys.executable, "main.py"],
        cwd=ROOT
    )

def run_streamlit():
    return subprocess.Popen(
        ["streamlit", "run", "streamlit_app.py"],
        cwd=ROOT
    )

if __name__ == "__main__":
    print("🚀 Starting Hexanova system...")

    backend = run_backend()
    frontend = run_streamlit()

    try:
        backend.wait()
        frontend.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        backend.terminate()
        frontend.terminate()
