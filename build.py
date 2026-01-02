import os
import subprocess
import sys

def build():
    print("Building FocusTimer.exe...")
    
    # Check if assets exist
    if not os.path.exists(os.path.join("assets", "icon.ico")):
        print("Warning: assets/icon.ico not found. Icon options might fail.")

    # Nuitka command
    # Using sys.executable ensures we use the same python interpreter (e.g. from conda env)
    command = [
        sys.executable, "-m", "nuitka",
        "--assume-yes-for-downloads",
        "--standalone",
        "--onefile",
        "--enable-plugin=tk-inter",
        "--windows-console-mode=disable",
        "--include-data-file=assets/icon.ico=assets/icon.ico",
        "--windows-icon-from-ico=assets/icon.ico",
        "--output-filename=FocusTimer.exe",
        "main.py"
    ]
    
    print(f"Running command: {' '.join(command)}")
    print("-" * 50)
    
    try:
        subprocess.check_call(command)
        print("-" * 50)
        print("\nBuild successful! -> FocusTimer.exe")
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build()
