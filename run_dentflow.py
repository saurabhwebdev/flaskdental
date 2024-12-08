import os
import sys
import webbrowser
import subprocess
import time
from pathlib import Path

def create_shortcut():
    try:
        import winshell
        from win32com.client import Dispatch
        
        # Get the path to the current script
        script_path = os.path.abspath(__file__)
        python_exe = sys.executable
        
        # Create desktop shortcut
        desktop = Path(winshell.desktop())
        path = os.path.join(desktop, "DentFlow Pro.lnk")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = python_exe
        shortcut.Arguments = f'"{script_path}"'
        shortcut.WorkingDirectory = os.path.dirname(script_path)
        shortcut.IconLocation = os.path.join(os.path.dirname(script_path), 'app', 'static', 'img', 'favicon.ico')
        shortcut.save()
        print("Desktop shortcut created successfully!")
    except Exception as e:
        print(f"Failed to create shortcut: {str(e)}")

def run_app():
    try:
        # Get the absolute path to the project directory
        project_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Activate virtual environment
        if sys.platform == "win32":
            venv_python = os.path.join(project_dir, "venv", "Scripts", "python.exe")
        else:
            venv_python = os.path.join(project_dir, "venv", "bin", "python")
            
        # Check if virtual environment exists
        if not os.path.exists(venv_python):
            print("Virtual environment not found. Please run the installation process first.")
            input("Press Enter to exit...")
            sys.exit(1)
            
        # Set Flask environment variables
        env = os.environ.copy()
        env["FLASK_APP"] = "app"
        
        # Start Flask application
        flask_process = subprocess.Popen(
            [venv_python, "-m", "flask", "run"],
            env=env,
            cwd=project_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for the server to start
        time.sleep(2)
        
        # Open web browser
        webbrowser.open('http://127.0.0.1:5000')
        
        print("DentFlow Pro is running!")
        print("Access the application at: http://127.0.0.1:5000")
        print("Press Ctrl+C to stop the server...")
        
        # Keep the script running and display Flask output
        while True:
            output = flask_process.stdout.readline()
            if output:
                print(output.strip())
            error = flask_process.stderr.readline()
            if error:
                print(error.strip(), file=sys.stderr)
            
            # Check if process is still running
            if flask_process.poll() is not None:
                break
                
    except KeyboardInterrupt:
        print("\nStopping DentFlow Pro...")
        flask_process.terminate()
        sys.exit(0)
    except Exception as e:
        print(f"Error: {str(e)}")
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--create-shortcut":
        create_shortcut()
    else:
        run_app()
