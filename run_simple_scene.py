#!/usr/bin/env python3
"""
Simple Scene Runner - Works with your existing character reference images
"""

import subprocess
import sys
from pathlib import Path

def find_blender():
    """Find Blender executable"""
    possible_paths = [
        "blender",
        "/Applications/Blender.app/Contents/MacOS/Blender",
        "/usr/local/bin/blender"
    ]
    
    for path in possible_paths:
        try:
            if Path(path).exists():
                return path
            result = subprocess.run([path, "--version"], capture_output=True, timeout=5)
            if result.returncode == 0:
                return path
        except:
            continue
    
    return None

def main():
    """Run the simple scene creator"""
    
    print("✨ LevlStudio Simple Scene Creator")
    print("Using character reference images as materials")
    print("=" * 50)
    
    # Find Blender
    blender_path = find_blender()
    
    if not blender_path:
        print("❌ Blender not found!")
        print("   Please install Blender from: https://www.blender.org/download/")
        return
    
    # Get script path
    script_path = Path(__file__).parent / "create_simple_scene.py"
    
    if not script_path.exists():
        print(f"❌ Script not found: {script_path}")
        return
    
    print(f"🎭 Found Blender at: {blender_path}")
    print(f"🚀 Running simple scene creator...")
    
    # Ask user preference
    mode = input("Run in background mode? (y/n, default=n): ").strip().lower()
    
    # Build command
    cmd = [blender_path]
    
    if mode == 'y':
        cmd.append("--background")
        print("🔄 Running in background mode...")
    else:
        print("🖼️ Opening Blender with scene...")
    
    cmd.extend(["--python", str(script_path)])
    
    try:
        print(f"⚡ Executing: {' '.join(cmd)}")
        result = subprocess.run(cmd, timeout=180)  # 3 minute timeout
        
        if result.returncode == 0:
            print("✅ Scene created successfully!")
            if mode != 'y':
                print("   Blender should now be open with your character scene")
                print("   Press F12 to render!")
        else:
            print(f"❌ Scene creation failed with code: {result.returncode}")
            
    except subprocess.TimeoutExpired:
        print("❌ Script timed out after 3 minutes")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()