#!/usr/bin/env python3
"""
Blender Debug Server Setup
Enables remote debugging with VS Code
"""

import sys
import os

def setup_debugger(port=5678):
    """Setup debugpy for remote debugging with VS Code"""
    try:
        import debugpy
    except ImportError:
        print("Installing debugpy...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "debugpy"])
        import debugpy
    
    # Enable debugging
    debugpy.listen(("localhost", port))
    print(f"Debugger listening on localhost:{port}")
    print("Attach VS Code debugger now...")
    
    # Optional: Wait for debugger to attach
    # debugpy.wait_for_client()
    
def main():
    """Main function to run in Blender"""
    import bpy
    
    # Setup debugger
    setup_debugger()
    
    # Your debugging code here
    print(f"Blender version: {bpy.app.version_string}")
    print(f"Python version: {sys.version}")
    print(f"Scene objects: {[obj.name for obj in bpy.context.scene.objects]}")
    
    # Set a breakpoint
    # debugpy.breakpoint()
    
    print("Debug server ready. You can now set breakpoints in VS Code.")

if __name__ == "__main__":
    main()
