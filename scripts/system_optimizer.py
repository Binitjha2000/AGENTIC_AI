import psutil
import os
import subprocess
from tkinter import messagebox

def optimize_system():
    results = []
    
    # Clean temp files
    temp_folders = [
        os.environ.get('TEMP', ''), 
        r'C:\Windows\Temp',
        os.path.expanduser('~\\AppData\\Local\\Temp')
    ]
    
    temp_folders = [folder for folder in temp_folders if folder and os.path.exists(folder)]
    
    for folder in temp_folders:
        try:
            files = os.listdir(folder)
            freed_space = sum(os.path.getsize(os.path.join(folder, f)) for f in files if os.path.exists(os.path.join(folder, f)))
            
            for f in files:
                file_path = os.path.join(folder, f)
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except PermissionError:
                        pass  # Ignore locked files
            
            results.append(f"🧹 Cleared {freed_space//1024//1024}MB from {folder}")
        except Exception as e:
            results.append(f"⚠️ Error cleaning {folder}: {str(e)}")

    # Visual effects adjustment (Non-blocking)
    subprocess.Popen('systempropertiesperformance.exe', shell=True)
    results.append("🎮 Opened visual effects settings (Set it to 'Best Performance' manually)")

    # Startup programs
    startup_path = os.path.expanduser('~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup')
    if os.path.exists(startup_path):
        for f in os.listdir(startup_path):
            file_path = os.path.join(startup_path, f)
            if f.endswith('.lnk') and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    results.append(f"🚀 Disabled startup program: {f}")
                except PermissionError:
                    results.append(f"⚠️ Could not remove startup program: {f}")

    return "\n".join(results)

if __name__ == "__main__":
    messagebox.showinfo("TurboCharge Results", optimize_system())
