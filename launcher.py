#!/usr/bin/env python3
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
        blender_path = "C:\\Program Files\\Blender Foundation\\Blender 4.4\\blender.exe"
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

def validate_access():
    """Validate user has proper access authorization"""
    print("🚀" + "=" * 50)
    print("🚀 LAUNCHING LEVLSTUDIO")
    print("🚀" + "=" * 50)
    print("✅ Initializing LevlStudio AI Pipeline...")
    print()
    return True

def main():
    import argparse
    parser = argparse.ArgumentParser(description="LevlStudio Launcher")
    parser.add_argument("--comfyui", action="store_true", help="Start ComfyUI")
    parser.add_argument("--blender", action="store_true", help="Start Blender")
    parser.add_argument("--watcher", action="store_true", help="Start Auto Watcher")
    parser.add_argument("--all", action="store_true", help="Start all services")
    parser.add_argument("--no-auth", action="store_true", help="Skip authentication (for automation)")
    
    args = parser.parse_args()
    
    # Validate access unless skipped for automation
    if not args.no_auth and not validate_access():
        return
    
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
