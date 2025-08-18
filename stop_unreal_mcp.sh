#!/bin/bash
# LevlStudio System Stop Script
# This script safely stops all LevlStudio services

echo "🛑 Stopping LevlStudio System..."

# Function to safely kill process
safe_kill() {
    local pid=$1
    local name=$2
    
    if [ ! -z "$pid" ] && kill -0 $pid 2>/dev/null; then
        echo "Stopping $name (PID: $pid)..."
        kill -TERM $pid 2>/dev/null
        
        # Wait up to 10 seconds for graceful shutdown
        local count=0
        while [ $count -lt 10 ] && kill -0 $pid 2>/dev/null; do
            sleep 1
            count=$((count + 1))
        done
        
        # Force kill if still running
        if kill -0 $pid 2>/dev/null; then
            echo "Force stopping $name..."
            kill -KILL $pid 2>/dev/null
        fi
        
        echo "✅ $name stopped"
    else
        echo "ℹ️  $name not running or already stopped"
    fi
}

# Read saved process IDs if available
if [ -f ".levlstudio_pids" ]; then
    echo "📋 Reading saved process IDs..."
    source .levlstudio_pids
fi

# Stop services in reverse order
echo "🔄 Stopping services..."

# Stop Dashboard Server
if [ ! -z "$DASHBOARD_PID" ]; then
    safe_kill "$DASHBOARD_PID" "Dashboard Server"
else
    # Find and stop by process name
    DASHBOARD_PIDS=$(ps aux | grep "dashboard-server.mjs" | grep -v grep | awk '{print $2}')
    for pid in $DASHBOARD_PIDS; do
        safe_kill "$pid" "Dashboard Server"
    done
fi

# Stop Blender
if [ ! -z "$BLENDER_PID" ]; then
    safe_kill "$BLENDER_PID" "Blender"
else
    # Find and stop by process name
    BLENDER_PIDS=$(ps aux | grep "levlstudio_scene_builder_addon.py" | grep -v grep | awk '{print $2}')
    for pid in $BLENDER_PIDS; do
        safe_kill "$pid" "Blender LevlStudio"
    done
fi

# Stop MCP Server
if [ ! -z "$MCP_PID" ]; then
    safe_kill "$MCP_PID" "MCP Server"
else
    # Find and stop by process name
    MCP_PIDS=$(ps aux | grep "mcp-server-filesystem" | grep -v grep | awk '{print $2}')
    for pid in $MCP_PIDS; do
        safe_kill "$pid" "MCP Server"
    done
fi

# Stop ComfyUI
if [ ! -z "$COMFYUI_PID" ]; then
    safe_kill "$COMFYUI_PID" "ComfyUI"
else
    # Find and stop ComfyUI processes
    COMFYUI_PIDS=$(ps aux | grep "main.py.*--port 8199" | grep -v grep | awk '{print $2}')
    for pid in $COMFYUI_PIDS; do
        safe_kill "$pid" "ComfyUI"
    done
fi

# Clean up any remaining processes
echo "🧹 Cleaning up remaining processes..."

# Kill any remaining Python processes that might be related
PYTHON_PIDS=$(ps aux | grep python | grep -E "(comfyui|levlstudio|mcp)" | grep -v grep | awk '{print $2}')
for pid in $PYTHON_PIDS; do
    if kill -0 $pid 2>/dev/null; then
        echo "Cleaning up Python process (PID: $pid)"
        kill -TERM $pid 2>/dev/null
    fi
done

# Kill any remaining Node processes that might be related
NODE_PIDS=$(ps aux | grep node | grep -E "(mcp-server|dashboard)" | grep -v grep | awk '{print $2}')
for pid in $NODE_PIDS; do
    if kill -0 $pid 2>/dev/null; then
        echo "Cleaning up Node process (PID: $pid)"
        kill -TERM $pid 2>/dev/null
    fi
done

echo "🔍 Final verification..."

# Check if services are actually stopped
REMAINING_SERVICES=()

if ps aux | grep "main.py.*--port 8199" | grep -v grep > /dev/null; then
    REMAINING_SERVICES+=("ComfyUI")
fi

if ps aux | grep "mcp-server-filesystem" | grep -v grep > /dev/null; then
    REMAINING_SERVICES+=("MCP Server")
fi

if ps aux | grep "levlstudio_scene_builder_addon" | grep -v grep > /dev/null; then
    REMAINING_SERVICES+=("Blender LevlStudio")
fi

if ps aux | grep "dashboard-server.mjs" | grep -v grep > /dev/null; then
    REMAINING_SERVICES+=("Dashboard Server")
fi

# Report status
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ ${#REMAINING_SERVICES[@]} -eq 0 ]; then
    echo "✅ All LevlStudio services stopped successfully"
    
    # Clean up PID file
    if [ -f ".levlstudio_pids" ]; then
        rm .levlstudio_pids
        echo "📋 Cleaned up process ID file"
    fi
else
    echo "⚠️  Some services may still be running:"
    for service in "${REMAINING_SERVICES[@]}"; do
        echo "   - $service"
    done
    echo ""
    echo "You may need to manually stop these processes or restart your system."
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🏁 LevlStudio System Stop Complete!"
echo ""
echo "💡 To restart the system, run: ./launch_levlstudio.sh"
echo "🆘 Need help? Check SYSTEM_LAUNCH_GUIDE.md"