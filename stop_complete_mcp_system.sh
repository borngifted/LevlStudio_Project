#!/bin/bash
# Complete LevlStudio + Unreal MCP System Stop Script

echo "🛑 Stopping Complete MCP System..."

PROJECT_ROOT="/Volumes/Jul_23_2025/LevlStudio_Project"
cd "$PROJECT_ROOT"

# Function to safely kill process
safe_kill() {
    local pid=$1
    local name=$2
    
    if [ ! -z "$pid" ] && kill -0 $pid 2>/dev/null; then
        echo "Stopping $name (PID: $pid)..."
        kill -TERM $pid 2>/dev/null
        
        local count=0
        while [ $count -lt 10 ] && kill -0 $pid 2>/dev/null; do
            sleep 1
            count=$((count + 1))
        done
        
        if kill -0 $pid 2>/dev/null; then
            echo "Force stopping $name..."
            kill -KILL $pid 2>/dev/null
        fi
        
        echo "✅ $name stopped"
    fi
}

# Read saved process IDs
if [ -f ".complete_system_pids" ]; then
    source .complete_system_pids
fi

echo "🔄 Stopping all MCP services..."

# Stop Unreal MCP Server
if [ ! -z "$UNREAL_MCP_PID" ]; then
    safe_kill "$UNREAL_MCP_PID" "Unreal MCP Server"
else
    UNREAL_PIDS=$(ps aux | grep "unreal_mcp_server_advanced.py" | grep -v grep | awk '{print $2}')
    for pid in $UNREAL_PIDS; do
        safe_kill "$pid" "Unreal MCP Server"
    done
fi

# Stop LevlStudio MCP Server
if [ ! -z "$LEVL_MCP_PID" ]; then
    safe_kill "$LEVL_MCP_PID" "LevlStudio MCP Server"
else
    LEVL_PIDS=$(ps aux | grep "levl_mcp_server.py" | grep -v grep | awk '{print $2}')
    for pid in $LEVL_PIDS; do
        safe_kill "$pid" "LevlStudio MCP Server"
    done
fi

# Stop Blender
if [ ! -z "$BLENDER_PID" ]; then
    safe_kill "$BLENDER_PID" "Blender"
else
    BLENDER_PIDS=$(ps aux | grep "levlstudio_scene_builder_addon.py" | grep -v grep | awk '{print $2}')
    for pid in $BLENDER_PIDS; do
        safe_kill "$pid" "Blender LevlStudio"
    done
fi

# Stop MCP Filesystem Server
if [ ! -z "$MCP_FS_PID" ]; then
    safe_kill "$MCP_FS_PID" "MCP Filesystem Server"
else
    MCP_PIDS=$(ps aux | grep "mcp-server-filesystem" | grep -v grep | awk '{print $2}')
    for pid in $MCP_PIDS; do
        safe_kill "$pid" "MCP Filesystem Server"
    done
fi

# Stop ComfyUI
if [ ! -z "$COMFYUI_PID" ]; then
    safe_kill "$COMFYUI_PID" "ComfyUI"
else
    COMFYUI_PIDS=$(ps aux | grep "main.py.*--port 8199" | grep -v grep | awk '{print $2}')
    for pid in $COMFYUI_PIDS; do
        safe_kill "$pid" "ComfyUI"
    done
fi

echo "🧹 Final cleanup..."

# Clean up any remaining related processes
PYTHON_PIDS=$(ps aux | grep python | grep -E "(comfyui|levlstudio|mcp|unreal)" | grep -v grep | awk '{print $2}')
for pid in $PYTHON_PIDS; do
    if kill -0 $pid 2>/dev/null; then
        echo "Cleaning up Python process (PID: $pid)"
        kill -TERM $pid 2>/dev/null
    fi
done

NODE_PIDS=$(ps aux | grep node | grep -E "(mcp-server)" | grep -v grep | awk '{print $2}')
for pid in $NODE_PIDS; do
    if kill -0 $pid 2>/dev/null; then
        echo "Cleaning up Node process (PID: $pid)"
        kill -TERM $pid 2>/dev/null
    fi
done

# Clean up PID file
if [ -f ".complete_system_pids" ]; then
    rm .complete_system_pids
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Complete MCP System stopped successfully"
echo "💡 To restart: ./start_complete_mcp_system.sh"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"