#!/usr/bin/env python3
"""
Start the LevlStudio MCP server with proper error handling
"""
import sys
import os
import traceback

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from levl_ue_to_comfy_oneclick_server import main
    print("🎬 Starting LevlStudio MCP Server...")
    print("📡 ComfyUI: http://127.0.0.1:8188")
    print("🔗 MCP Server: http://127.0.0.1:8765")
    print("=" * 50)
    
    # Override sys.argv to provide correct arguments
    sys.argv = [
        'levl_ue_to_comfy_oneclick_server.py',
        '--host', '127.0.0.1',
        '--port', '8765', 
        '--comfy_host', '127.0.0.1',
        '--comfy_port', '8188'
    ]
    
    main()
    
except KeyboardInterrupt:
    print("\n👋 Server stopped by user")
except Exception as e:
    print(f"❌ Server error: {e}")
    traceback.print_exc()
    sys.exit(1)