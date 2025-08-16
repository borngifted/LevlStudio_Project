#!/usr/bin/env python3
"""
Blender Scene Runner for LevlStudio
Easy interface to run different Blender scene creation scripts
"""

import subprocess
import sys
import os
from pathlib import Path

def find_blender():
    """Find Blender executable"""
    possible_paths = [
        "blender",
        "/Applications/Blender.app/Contents/MacOS/Blender",
        "/usr/local/bin/blender",
        "C:\\Program Files\\Blender Foundation\\Blender\\blender.exe"
    ]
    
    for path in possible_paths:
        try:
            if Path(path).exists():
                return path
            # Try running it to see if it's in PATH
            result = subprocess.run([path, "--version"], capture_output=True, timeout=5)
            if result.returncode == 0:
                return path
        except:
            continue
    
    return None

def run_blender_script(script_path, background=True):
    """Run a Blender script"""
    blender_path = find_blender()
    
    if not blender_path:
        print("❌ Blender not found!")
        print("   Please install Blender or add it to your PATH")
        print("   Download from: https://www.blender.org/download/")
        return False
    
    print(f"🎭 Found Blender at: {blender_path}")
    print(f"🚀 Running script: {script_path}")
    
    # Build command
    cmd = [blender_path]
    
    if background:
        cmd.append("--background")
    
    cmd.extend(["--python", str(script_path)])
    
    try:
        print(f"⚡ Executing: {' '.join(cmd)}")
        result = subprocess.run(cmd, timeout=300)  # 5 minute timeout
        
        if result.returncode == 0:
            print("✅ Script completed successfully!")
            return True
        else:
            print(f"❌ Script failed with code: {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Script timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Error running script: {e}")
        return False

def main():
    """Main interface for running Blender scenes"""
    
    print("🎭 LevlStudio Blender Scene Runner")
    print("=" * 40)
    
    # Get project directory
    project_dir = Path(__file__).parent
    
    # Available scene scripts
    scenes = {
        "1": {
            "name": "Christmas Scene",
            "script": "create_christmas_scene.py",
            "description": "Christmas scene with characters, trees, and festive lighting"
        },
        "2": {
            "name": "Character Showcase", 
            "script": "create_character_showcase.py",
            "description": "Circular arrangement of all available characters"
        }
    }
    
    print("\n📋 Available scenes:")
    for key, scene in scenes.items():
        print(f"   {key}. {scene['name']}")
        print(f"      {scene['description']}")
    
    print("\n🎯 Options:")
    print("   h - Show this help")
    print("   q - Quit")
    
    while True:
        choice = input("\n👉 Select a scene (1-2) or option (h/q): ").strip().lower()
        
        if choice == 'q':
            print("👋 Goodbye!")
            break
            
        elif choice == 'h':
            print("\n📖 How to use:")
            print("1. Select a scene number")
            print("2. The script will run in Blender")
            print("3. Blender will open with your scene loaded")
            print("4. Press F12 to render an image")
            print("5. Press Ctrl+F12 to render animation")
            continue
            
        elif choice in scenes:
            scene = scenes[choice]
            script_path = project_dir / scene["script"]
            
            if not script_path.exists():
                print(f"❌ Script not found: {script_path}")
                continue
            
            print(f"\n🎬 Creating {scene['name']}...")
            
            # Ask if user wants background mode
            bg_choice = input("Run in background mode? (y/n, default=n): ").strip().lower()
            background = bg_choice == 'y'
            
            if background:
                print("🔄 Running in background mode...")
            else:
                print("🖼️ Running with Blender UI...")
            
            success = run_blender_script(script_path, background=background)
            
            if success:
                print(f"🎉 {scene['name']} created successfully!")
                if not background:
                    print("   Blender should now be open with your scene")
                    print("   Press F12 to render!")
            else:
                print(f"❌ Failed to create {scene['name']}")
        
        else:
            print("❌ Invalid choice. Please select 1-2, h, or q")

def command_line_interface():
    """Command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LevlStudio Blender Scene Runner")
    parser.add_argument("--scene", choices=["christmas", "showcase"], 
                       help="Scene to create")
    parser.add_argument("--background", action="store_true",
                       help="Run in background mode")
    parser.add_argument("--list", action="store_true",
                       help="List available scenes")
    
    args = parser.parse_args()
    
    if args.list:
        print("Available scenes:")
        print("  christmas - Christmas scene with characters and environment")
        print("  showcase - Character showcase in circular arrangement")
        return
    
    if args.scene:
        project_dir = Path(__file__).parent
        
        if args.scene == "christmas":
            script_path = project_dir / "create_christmas_scene.py"
        elif args.scene == "showcase":
            script_path = project_dir / "create_character_showcase.py"
        
        if script_path.exists():
            run_blender_script(script_path, background=args.background)
        else:
            print(f"❌ Scene script not found: {script_path}")
    else:
        # Run interactive mode
        main()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command_line_interface()
    else:
        main()