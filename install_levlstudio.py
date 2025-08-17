#!/usr/bin/env python3
"""
LevlStudio One-Click Installer
Cross-platform installer for Mac and Windows
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path
import urllib.request
import zipfile
import json

class LevlStudioInstaller:
    def __init__(self):
        self.system = platform.system()
        self.project_root = Path(__file__).parent
        self.is_mac = self.system == "Darwin"
        self.is_windows = self.system == "Windows"
        self.is_linux = self.system == "Linux"
        
        # Detect ComfyUI location
        self.comfyui_path = self.detect_comfyui_path()
        
    def detect_comfyui_path(self):
        """Detect or set ComfyUI installation path"""
        # Check local ComfyUI folder first
        local_comfyui = self.project_root / "ComfyUI"
        if local_comfyui.exists():
            return local_comfyui
            
        # Platform-specific default paths
        if self.is_mac:
            return Path("/Users") / os.getenv("USER", "user") / "ComfyUI" / "ComfyUI"
        elif self.is_windows:
            return Path(os.getenv("USERPROFILE", "C:\\Users\\User")) / "ComfyUI" / "ComfyUI"
        else:
            return Path.home() / "ComfyUI" / "ComfyUI"
    
    def print_header(self):
        """Print installation header"""
        print("🎬" + "=" * 60)
        print("🎬 LevlStudio One-Click Installer")
        print("🎬 AI-Powered 3D Content Creation Pipeline")
        print("🎬" + "=" * 60)
        print(f"🖥️  Platform: {self.system}")
        print(f"📁 Project: {self.project_root}")
        print(f"🎨 ComfyUI: {self.comfyui_path}")
        print()
    
    def check_prerequisites(self):
        """Check system prerequisites"""
        print("🔍 Checking Prerequisites...")
        
        # Check Python
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            print("❌ Python 3.8+ required")
            return False
        print(f"✅ Python {python_version.major}.{python_version.minor}")
        
        # Check Git
        try:
            subprocess.run(["git", "--version"], capture_output=True, check=True)
            print("✅ Git installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Git not found - please install Git first")
            return False
        
        # Check Blender
        blender_paths = self.get_blender_paths()
        blender_found = False
        for blender_path in blender_paths:
            if Path(blender_path).exists():
                print(f"✅ Blender found: {blender_path}")
                blender_found = True
                break
        
        if not blender_found:
            print("⚠️  Blender not found - install from https://www.blender.org/download/")
            print("   (Optional - some features will be unavailable)")
        
        return True
    
    def get_blender_paths(self):
        """Get platform-specific Blender paths"""
        if self.is_mac:
            return ["/Applications/Blender.app/Contents/MacOS/Blender"]
        elif self.is_windows:
            return [
                "C:\\Program Files\\Blender Foundation\\Blender 4.4\\blender.exe",
                "C:\\Program Files\\Blender Foundation\\Blender 4.3\\blender.exe",
                "C:\\Program Files\\Blender Foundation\\Blender 4.2\\blender.exe",
            ]
        else:
            return ["blender", "/usr/bin/blender", "/usr/local/bin/blender"]
    
    def setup_python_environment(self):
        """Set up Python virtual environment"""
        print("🐍 Setting up Python Environment...")
        
        venv_path = self.project_root / ".venv"
        
        if not venv_path.exists():
            print("📦 Creating virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        
        # Get activation script path
        if self.is_windows:
            activate_script = venv_path / "Scripts" / "activate.bat"
            python_exe = venv_path / "Scripts" / "python.exe"
        else:
            activate_script = venv_path / "bin" / "activate"
            python_exe = venv_path / "bin" / "python"
        
        print("📦 Installing Python dependencies...")
        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            subprocess.run([str(python_exe), "-m", "pip", "install", "-r", str(requirements_file)], check=True)
        
        print("✅ Python environment ready")
        return python_exe, activate_script
    
    def setup_comfyui(self):
        """Set up ComfyUI integration"""
        print("🎨 Setting up ComfyUI Integration...")
        
        # Check if local ComfyUI exists
        local_comfyui = self.project_root / "ComfyUI"
        if local_comfyui.exists():
            print(f"✅ Using local ComfyUI at: {local_comfyui}")
            self.comfyui_path = local_comfyui
        else:
            # Check if ComfyUI exists at detected path
            if not self.comfyui_path.exists():
                print(f"📥 ComfyUI not found at {self.comfyui_path}")
                response = input("Would you like to download ComfyUI? (y/n): ")
                if response.lower() == 'y':
                    self.download_comfyui()
                else:
                    print("⚠️  ComfyUI features will be unavailable")
                    return False
        
        # Install ComfyUI extensions
        self.install_comfyui_extensions()
        return True
    
    def download_comfyui(self):
        """Download and set up ComfyUI"""
        print("📥 Downloading ComfyUI...")
        
        # Create ComfyUI directory
        comfyui_parent = self.comfyui_path.parent
        comfyui_parent.mkdir(parents=True, exist_ok=True)
        
        # Clone ComfyUI repository
        subprocess.run([
            "git", "clone", "https://github.com/comfyanonymous/ComfyUI.git",
            str(self.comfyui_path)
        ], check=True)
        
        # Install ComfyUI requirements
        requirements_file = self.comfyui_path / "requirements.txt"
        if requirements_file.exists():
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], check=True)
        
        print("✅ ComfyUI downloaded and set up")
    
    def install_comfyui_extensions(self):
        """Install required ComfyUI extensions"""
        print("🔌 Installing ComfyUI Extensions...")
        
        custom_nodes = self.comfyui_path / "custom_nodes"
        custom_nodes.mkdir(exist_ok=True)
        
        extensions = [
            {
                "name": "ControlNet Aux",
                "repo": "https://github.com/Fannovel16/comfyui_controlnet_aux.git",
                "folder": "comfyui_controlnet_aux"
            },
            {
                "name": "Video Helper Suite", 
                "repo": "https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git",
                "folder": "ComfyUI-VideoHelperSuite"
            },
            {
                "name": "Advanced ControlNet",
                "repo": "https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet.git",
                "folder": "ComfyUI-Advanced-ControlNet"
            }
        ]
        
        for ext in extensions:
            ext_path = custom_nodes / ext["folder"]
            if not ext_path.exists():
                print(f"📦 Installing {ext['name']}...")
                subprocess.run([
                    "git", "clone", ext["repo"], str(ext_path)
                ], check=True)
            else:
                print(f"✅ {ext['name']} already installed")
        
        print("✅ ComfyUI extensions installed")
    
    def setup_blender_integration(self):
        """Set up Blender addon integration"""
        print("🎭 Setting up Blender Integration...")
        
        addon_file = self.project_root / "levlstudio_scene_builder_addon.py"
        if not addon_file.exists():
            print("⚠️  Blender addon not found - some features unavailable")
            return False
        
        # Find Blender addon directory
        blender_paths = self.get_blender_paths()
        for blender_path in blender_paths:
            if Path(blender_path).exists():
                if self.is_mac:
                    addon_dir = Path.home() / "Library/Application Support/Blender/4.4/scripts/addons"
                elif self.is_windows:
                    addon_dir = Path(os.getenv("APPDATA")) / "Blender Foundation/Blender/4.4/scripts/addons"
                else:
                    addon_dir = Path.home() / ".config/blender/4.4/scripts/addons"
                
                addon_dir.mkdir(parents=True, exist_ok=True)
                
                # Copy addon
                target_addon = addon_dir / "levlstudio_scene_builder_addon.py"
                shutil.copy2(addon_file, target_addon)
                print(f"✅ Blender addon installed to: {target_addon}")
                return True
        
        print("⚠️  Blender not found - addon installation skipped")
        return False
    
    def create_startup_scripts(self):
        """Create platform-specific startup scripts"""
        print("📝 Creating Startup Scripts...")
        
        # Cross-platform Python launcher
        launcher_content = f'''#!/usr/bin/env python3
"""
LevlStudio Launcher
Cross-platform startup script
"""

import os
import sys
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
COMFYUI_PATH = PROJECT_ROOT / "ComfyUI"

def start_comfyui():
    """Start ComfyUI server"""
    print("🎨 Starting ComfyUI...")
    if COMFYUI_PATH.exists():
        os.chdir(COMFYUI_PATH)
        subprocess.run([sys.executable, "main.py"])
    else:
        print("❌ ComfyUI not found")

def start_blender():
    """Start Blender with addon"""
    print("🎭 Starting Blender...")
    addon_file = PROJECT_ROOT / "levlstudio_scene_builder_addon.py"
    
    if sys.platform == "darwin":  # Mac
        blender_path = "/Applications/Blender.app/Contents/MacOS/Blender"
    elif sys.platform == "win32":  # Windows
        blender_path = "C:\\\\Program Files\\\\Blender Foundation\\\\Blender 4.4\\\\blender.exe"
    else:  # Linux
        blender_path = "blender"
    
    if Path(blender_path).exists():
        subprocess.run([blender_path, "--python", str(addon_file)])
    else:
        print("❌ Blender not found")

def start_auto_watcher():
    """Start auto git watcher"""
    print("🔍 Starting Auto Git Watcher...")
    watcher_file = PROJECT_ROOT / "auto_git_watcher.py"
    if watcher_file.exists():
        subprocess.run([sys.executable, str(watcher_file)])

def main():
    import argparse
    parser = argparse.ArgumentParser(description="LevlStudio Launcher")
    parser.add_argument("--comfyui", action="store_true", help="Start ComfyUI")
    parser.add_argument("--blender", action="store_true", help="Start Blender")
    parser.add_argument("--watcher", action="store_true", help="Start Auto Watcher")
    parser.add_argument("--all", action="store_true", help="Start all services")
    
    args = parser.parse_args()
    
    if args.comfyui or args.all:
        start_comfyui()
    elif args.blender or args.all:
        start_blender()
    elif args.watcher or args.all:
        start_auto_watcher()
    else:
        print("🎬 LevlStudio Launcher")
        print("Usage:")
        print("  python launcher.py --comfyui   # Start ComfyUI")
        print("  python launcher.py --blender   # Start Blender")
        print("  python launcher.py --watcher   # Start Auto Watcher")

if __name__ == "__main__":
    main()
'''
        
        launcher_file = self.project_root / "launcher.py"
        with open(launcher_file, 'w') as f:
            f.write(launcher_content)
        os.chmod(launcher_file, 0o755)
        
        # Windows batch file
        if self.is_windows:
            batch_content = f'''@echo off
echo 🎬 LevlStudio Launcher - Windows
cd /d "{self.project_root}"
python launcher.py %*
pause
'''
            batch_file = self.project_root / "LevlStudio.bat"
            with open(batch_file, 'w') as f:
                f.write(batch_content)
        
        # Mac/Linux shell script
        else:
            shell_content = f'''#!/bin/bash
echo "🎬 LevlStudio Launcher - {self.system}"
cd "{self.project_root}"
python3 launcher.py "$@"
'''
            shell_file = self.project_root / "LevlStudio.sh"
            with open(shell_file, 'w') as f:
                f.write(shell_content)
            os.chmod(shell_file, 0o755)
        
        print("✅ Startup scripts created")
    
    def create_config_file(self):
        """Create configuration file"""
        print("⚙️ Creating Configuration...")
        
        config = {
            "platform": self.system,
            "project_root": str(self.project_root),
            "comfyui_path": str(self.comfyui_path),
            "blender_paths": self.get_blender_paths(),
            "python_executable": sys.executable,
            "installation_date": str(Path(__file__).stat().st_mtime),
            "version": "2.0.0"
        }
        
        config_file = self.project_root / "levlstudio_config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Configuration saved to: {config_file}")
    
    def install(self):
        """Run complete installation"""
        self.print_header()
        
        if not self.check_prerequisites():
            print("❌ Prerequisites not met - installation aborted")
            return False
        
        try:
            python_exe, activate_script = self.setup_python_environment()
            self.setup_comfyui()
            self.setup_blender_integration() 
            self.create_startup_scripts()
            self.create_config_file()
            
            print("\n🎉" + "=" * 60)
            print("🎉 LevlStudio Installation Complete!")
            print("🎉" + "=" * 60)
            print("\n🚀 Quick Start:")
            print(f"   ComfyUI:     python launcher.py --comfyui")
            print(f"   Blender:     python launcher.py --blender") 
            print(f"   Auto-Watch:  python launcher.py --watcher")
            print(f"\n📁 Project: {self.project_root}")
            print(f"🎨 ComfyUI: {self.comfyui_path}")
            print(f"\n📖 Documentation:")
            print(f"   Setup:       SETUP_INSTRUCTIONS.md")
            print(f"   Complete:    COMPLETE_PROJECT_GUIDE.md")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Installation failed: {e}")
            return False

def main():
    installer = LevlStudioInstaller()
    success = installer.install()
    
    if success:
        print("\n✨ Ready to create AI-powered 3D content!")
    else:
        print("\n💥 Installation failed - check error messages above")
        sys.exit(1)

if __name__ == "__main__":
    main()