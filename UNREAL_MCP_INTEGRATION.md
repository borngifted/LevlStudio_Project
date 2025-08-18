# LevlStudio System Launch Guide

This guide covers the complete system launch procedure for the LevlStudio integration with ComfyUI, Blender, and MCP services.

## System Overview

The LevlStudio system consists of several interconnected services:
- **ComfyUI Server** - AI image/video generation
- **MCP Filesystem Server** - File system operations
- **Blender Integration** - 3D asset creation and scene building
- **Dashboard Server** - Web interface
- **Unreal Engine MCP Bridge** - Real-time engine control

## Pre-Launch System Check

Run this command to verify all required processes are running:

```bash
# Check for running services
ps aux | grep -E "(python|node|comfyui|mcp|blender)" | grep -v grep
```

Expected processes:
- ComfyUI on port 8188/8199
- MCP filesystem server
- Node dashboard server
- Blender with LevlStudio addon

## Automated System Launch

### Quick Start Script
Create and run this launch script:

```bash
#!/bin/bash
# save as: launch_levlstudio.sh

echo "🚀 Launching LevlStudio System..."

# Check if ComfyUI is running
if ! curl -s http://127.0.0.1:8199/queue > /dev/null; then
    echo "⚠️  ComfyUI not detected on port 8199"
    echo "Starting ComfyUI..."
    cd ComfyUI/ComfyUI
    source venv/bin/activate
    python main.py --port 8199 &
    sleep 5
fi

# Check MCP server
if ! ps aux | grep "mcp-server-filesystem" | grep -v grep > /dev/null; then
    echo "⚠️  MCP server not running"
    echo "Starting MCP server..."
    npx @modelcontextprotocol/server-filesystem /Users/$USER &
    sleep 2
fi

# Check Blender addon
if ! ps aux | grep "levlstudio_scene_builder_addon.py" | grep -v grep > /dev/null; then
    echo "⚠️  Blender addon not running"
    echo "Starting Blender with LevlStudio addon..."
    /Applications/Blender.app/Contents/MacOS/Blender --python levlstudio_scene_builder_addon.py &
    sleep 3
fi

# Health check
echo "🔍 System Health Check:"

# Test ComfyUI
if curl -s http://127.0.0.1:8199/queue > /dev/null; then
    echo "✅ ComfyUI: Running (port 8199)"
else
    echo "❌ ComfyUI: Failed"
fi

# Test MCP
if ps aux | grep "mcp-server-filesystem" | grep -v grep > /dev/null; then
    echo "✅ MCP Server: Running"
else
    echo "❌ MCP Server: Failed"
fi

# Test Blender
if ps aux | grep "levlstudio_scene_builder_addon" | grep -v grep > /dev/null; then
    echo "✅ Blender: Running with LevlStudio addon"
else
    echo "❌ Blender: Failed"
fi

echo "🎯 System launch complete! Ready for Unreal Engine integration."
```

Make executable and run:
```bash
chmod +x launch_levlstudio.sh
./launch_levlstudio.sh
```

## Manual Launch Procedure

### 1. ComfyUI Server
```bash
cd ComfyUI/ComfyUI
source venv/bin/activate
python main.py --port 8199
```

### 2. MCP Filesystem Server
```bash
npx @modelcontextprotocol/server-filesystem /Users/$USER
```

### 3. Blender with LevlStudio Addon
```bash
/Applications/Blender.app/Contents/MacOS/Blender --python levlstudio_scene_builder_addon.py
```

### 4. Dashboard Server (Optional)
```bash
node dashboard-server.mjs
```

## System Health Verification

### ComfyUI Health Check
```bash
# Check system stats
curl -s http://127.0.0.1:8199/system_stats | jq

# Check queue status
curl -s http://127.0.0.1:8199/queue | jq

# Expected Response:
# {"queue_running": [], "queue_pending": []}
```

### MCP Server Health Check
```bash
# Verify MCP process
ps aux | grep "mcp-server-filesystem" | grep -v grep

# Should return:
# node /path/to/.npm/_npx/.../mcp-server-filesystem /Users/username
```

### Blender Integration Check
```bash
# Verify Blender addon
ps aux | grep "levlstudio_scene_builder_addon" | grep -v grep

# Check Blender process
ps aux | grep "Blender.*--python levlstudio_scene_builder_addon.py" | grep -v grep
```

## Integration with Unreal Engine MCP

Once all services are running, configure the Unreal Engine MCP connection:

### 1. Unreal MCP Configuration
Add to your MCP client configuration (`.cursor/mcp.json`, `~/.config/claude-desktop/mcp.json`):

```json
{
  "mcpServers": {
    "unrealMCP": {
      "command": "uv",
      "args": [
        "--directory", 
        "/path/to/unreal-engine-mcp/Python",
        "run", 
        "unreal_mcp_server_advanced.py"
      ]
    },
    "levlstudio": {
      "command": "python",
      "args": [
        "/path/to/LevlStudio_Project/levl_mcp_server.py"
      ]
    }
  }
}
```

### 2. Test Integration
```bash
# Test the full pipeline
python test_full_integration.py

# Or manually test:
# 1. Generate image in ComfyUI
# 2. Process in Blender
# 3. Export to Unreal Engine
```

## Troubleshooting

### Port Conflicts
```bash
# Check what's using ports 8188/8199
lsof -i :8188
lsof -i :8199

# Kill conflicting processes if needed
kill -9 $(lsof -t -i :8199)
```

### Service Restart
```bash
# Kill all related processes
pkill -f "comfyui\|mcp-server\|blender.*levlstudio"

# Wait 5 seconds then restart
sleep 5
./launch_levlstudio.sh
```

### Log Files
Check logs for debugging:
- ComfyUI: `ComfyUI/ComfyUI/user/comfyui_8199.log`
- System logs: `/var/log/system.log`
- Application crashes: `~/Library/Logs/DiagnosticReports/`

## Performance Optimization

### Resource Monitoring
```bash
# Monitor system resources
top -pid $(pgrep -f "comfyui\|mcp-server\|blender")

# Check memory usage
ps aux | grep -E "(comfyui|mcp-server|blender)" | awk '{print $2, $3, $4, $11}'
```

### Recommended System Requirements
- **RAM**: 16GB+ (32GB recommended)
- **GPU**: Metal-compatible GPU for ComfyUI acceleration
- **Storage**: 50GB+ free space for models and assets
- **CPU**: Apple Silicon M1/M2/M3 or Intel i7+

## Advanced Configuration

### Environment Variables
```bash
export COMFYUI_PORT=8199
export MCP_SERVER_PATH="/Users/$USER"
export BLENDER_PATH="/Applications/Blender.app/Contents/MacOS/Blender"
export LEVLSTUDIO_ADDON_PATH="/path/to/levlstudio_scene_builder_addon.py"
```

### Custom Launch Configuration
Create `levlstudio_config.json`:
```json
{
  "services": {
    "comfyui": {
      "enabled": true,
      "port": 8199,
      "auto_start": true
    },
    "mcp_server": {
      "enabled": true,
      "root_path": "/Users/username",
      "auto_start": true
    },
    "blender": {
      "enabled": true,
      "addon_path": "levlstudio_scene_builder_addon.py",
      "auto_start": true
    }
  }
}
```

## Support

For issues with the system launch:
1. Check the [Troubleshooting](#troubleshooting) section
2. Join our [Discord](https://discord.gg/3KNkke3rnH)
3. Review system logs
4. File an issue on GitHub with system information

---

**Next Steps**: Once all services are running, proceed to [Unreal Engine Integration](README.md#lightning-fast-setup) for connecting with the MCP server.