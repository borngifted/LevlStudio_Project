#!/usr/bin/env python3
"""
Quick start script for LevlStudio Scene Builder (Python version for cross-platform)
"""

import subprocess
import sys
import os
from pathlib import Path
import platform

def check_blender():
    """Check if Blender is installed"""
    try:
        result = subprocess.run(['blender', '--version'], capture_output=True, text=True)
        version = result.stdout.split('\n')[0].split()[-1]
        print(f"✅ Blender found: version {version}")
        return True
    except FileNotFoundError:
        print("❌ Blender not found. Please install Blender first.")
        print("   Download from: https://www.blender.org/download/")
        return False

def get_addon_directory():
    """Get Blender addon directory based on OS"""
    system = platform.system()
    home = Path.home()
    
    if system == "Darwin":  # macOS
        return home / "Library/Application Support/Blender/3.6/scripts/addons"
    elif system == "Windows":
        return home / "AppData/Roaming/Blender Foundation/Blender/3.6/scripts/addons"
    else:  # Linux
        return home / ".config/blender/3.6/scripts/addons"

def main_menu():
    """Display main menu and get user choice"""
    print("\n🎬 LevlStudio Scene Builder - Quick Start")
    print("=" * 50)
    print("\n🚀 What would you like to do?\n")
    print("1) Open Blender with the addon")
    print("2) Install addon to Blender's addon folder")
    print("3) Run batch processing (all scenes)")
    print("4) Build specific scene (headless)")
    print("5) Install Python dependencies")
    print("6) Test addon loading")
    print("0) Exit\n")
    
    choice = input("Enter choice (0-6): ")
    return choice

def execute_choice(choice):
    """Execute user's choice"""
    project_dir = Path(__file__).parent
    
    if choice == "1":
        print("\nOpening Blender with LevlStudio addon...")
        subprocess.run(['blender', '--python', 'levlstudio_scene_builder_addon.py'])
    
    elif choice == "2":
        print("\nInstalling addon to Blender...")
        addon_dir = get_addon_directory()
        addon_dir.mkdir(parents=True, exist_ok=True)
        
        source = project_dir / "levlstudio_scene_builder_addon.py"
        dest = addon_dir / "levlstudio_scene_builder_addon.py"
        
        import shutil
        shutil.copy2(source, dest)
        print(f"✅ Addon installed to: {dest}")
        print("   Enable it in Blender: Edit → Preferences → Add-ons → Search 'LevlStudio'")
    
    elif choice == "3":
        print("\nRunning batch processing...")
        subprocess.run(['blender', '-b', '--python', 'batch_process.py', '--', '--batch'])
    
    elif choice == "4":
        scene_idx = input("Enter scene index (0-2): ")
        print(f"\nBuilding scene {scene_idx}...")
        subprocess.run([
            'blender', '-b', '--python', 'batch_process.py', '--',
            '--scene', scene_idx,
            '--export', f'exports/scene_{scene_idx}.glb',
            '--render', f'renders/scene_{scene_idx}.png'
        ])
    
    elif choice == "5":
        print("\nInstalling Python dependencies...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed")
    
    elif choice == "6":
        print("\nTesting addon loading...")
        test_code = """
import bpy
import sys
sys.path.append('.')
import levlstudio_scene_builder_addon
levlstudio_scene_builder_addon.register()
print('✅ Addon loaded successfully!')
"""
        subprocess.run(['blender', '-b', '--python-expr', test_code])
    
    elif choice == "0":
        print("\n👋 Goodbye!")
        sys.exit(0)
    
    else:
        print("\n❌ Invalid choice")

def main():
    """Main entry point"""
    print("🎬 LevlStudio Scene Builder - Setup Assistant")
    print("=" * 50)
    
    # Check for Blender
    if not check_blender():
        sys.exit(1)
    
    # Main loop
    while True:
        choice = main_menu()
        execute_choice(choice)
        
        if choice != "0":
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
