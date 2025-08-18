#!/bin/bash
# LevlStudio System Launch Script
# This script launches all required services for the LevlStudio integration

echo "🚀 Launching LevlStudio System..."

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to wait for a service to be ready
wait_for_service() {
    local url=$1
    local timeout=${2:-30}
    local count=0
    
    echo "⏳ Waiting for service at $url..."
    while [ $count -lt $timeout ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo "✅ Service ready at $url"
            return 0
        fi
        sleep 1
        count=$((count + 1))
    done
    
    echo "❌ Service failed to start at $url"
    return 1
}

# 1. Check and start ComfyUI
echo "📊 Checking ComfyUI..."
if check_port 8199; then
    echo "✅ ComfyUI already running on port 8199"
else
    echo "⚠️  ComfyUI not detected on port 8199"
    
    # Check if ComfyUI directory exists
    if [ -d "ComfyUI/ComfyUI" ]; then
        echo "Starting ComfyUI..."
        cd ComfyUI/ComfyUI
        
        # Activate virtual environment if it exists
        if [ -d "venv" ]; then
            source venv/bin/activate
        fi
        
        # Start ComfyUI in background
        python main.py --port 8199 > /dev/null 2>&1 &
        COMFYUI_PID=$!
        cd - > /dev/null
        
        # Wait for ComfyUI to be ready
        if wait_for_service "http://127.0.0.1:8199/queue" 30; then
            echo "✅ ComfyUI started successfully (PID: $COMFYUI_PID)"
        else
            echo "❌ ComfyUI failed to start"
        fi
    else
        echo "❌ ComfyUI directory not found. Please ensure ComfyUI is installed."
    fi
fi

# 2. Check and start MCP Filesystem Server
echo "📁 Checking MCP Filesystem Server..."
if ps aux | grep "mcp-server-filesystem" | grep -v grep > /dev/null; then
    echo "✅ MCP Server already running"
else
    echo "⚠️  MCP server not running"
    echo "Starting MCP server..."
    
    # Start MCP server in background
    npx @modelcontextprotocol/server-filesystem "$HOME" > /dev/null 2>&1 &
    MCP_PID=$!
    
    # Give it a moment to start
    sleep 3
    
    if ps aux | grep "mcp-server-filesystem" | grep -v grep > /dev/null; then
        echo "✅ MCP Server started successfully (PID: $MCP_PID)"
    else
        echo "❌ MCP Server failed to start"
    fi
fi

# 3. Check and start Blender with LevlStudio addon
echo "🎨 Checking Blender LevlStudio addon..."
if ps aux | grep "levlstudio_scene_builder_addon.py" | grep -v grep > /dev/null; then
    echo "✅ Blender already running with LevlStudio addon"
else
    echo "⚠️  Blender addon not running"
    
    # Check if addon file exists
    if [ -f "levlstudio_scene_builder_addon.py" ]; then
        echo "Starting Blender with LevlStudio addon..."
        
        # Start Blender with addon in background
        /Applications/Blender.app/Contents/MacOS/Blender --python levlstudio_scene_builder_addon.py > /dev/null 2>&1 &
        BLENDER_PID=$!
        
        # Give Blender time to load
        sleep 5
        
        if ps aux | grep "levlstudio_scene_builder_addon" | grep -v grep > /dev/null; then
            echo "✅ Blender started with LevlStudio addon (PID: $BLENDER_PID)"
        else
            echo "❌ Blender failed to start with addon"
        fi
    else
        echo "❌ LevlStudio addon file not found"
    fi
fi

# 4. Optional: Start Dashboard Server
echo "📈 Checking Dashboard Server..."
if ps aux | grep "dashboard-server.mjs" | grep -v grep > /dev/null; then
    echo "✅ Dashboard Server already running"
else
    if [ -f "dashboard-server.mjs" ]; then
        echo "Starting Dashboard Server..."
        node dashboard-server.mjs > /dev/null 2>&1 &
        DASHBOARD_PID=$!
        echo "✅ Dashboard Server started (PID: $DASHBOARD_PID)"
    else
        echo "ℹ️  Dashboard Server file not found (optional service)"
    fi
fi

echo ""
echo "🔍 Final System Health Check:"

# Health checks
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ComfyUI health check
if curl -s http://127.0.0.1:8199/queue > /dev/null 2>&1; then
    queue_status=$(curl -s http://127.0.0.1:8199/queue | grep -o '"queue_running":\[\]' || echo "active")
    if [[ $queue_status == *"[]"* ]]; then
        echo "✅ ComfyUI: Running and ready (port 8199, queue empty)"
    else
        echo "⚠️  ComfyUI: Running but queue active (port 8199)"
    fi
else
    echo "❌ ComfyUI: Not responding on port 8199"
fi

# MCP Server health check
if ps aux | grep "mcp-server-filesystem" | grep -v grep > /dev/null; then
    echo "✅ MCP Server: Running (filesystem access enabled)"
else
    echo "❌ MCP Server: Not running"
fi

# Blender health check
if ps aux | grep "levlstudio_scene_builder_addon" | grep -v grep > /dev/null; then
    echo "✅ Blender: Running with LevlStudio addon"
else
    echo "❌ Blender: Not running with LevlStudio addon"
fi

# Dashboard health check
if ps aux | grep "dashboard-server.mjs" | grep -v grep > /dev/null; then
    echo "✅ Dashboard: Running (web interface available)"
else
    echo "ℹ️  Dashboard: Not running (optional)"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Final status
echo ""
echo "🎯 LevlStudio System Launch Complete!"
echo ""
echo "📝 Next Steps:"
echo "   1. Configure your MCP client (see README.md)"
echo "   2. Test Unreal Engine connection"
echo "   3. Run: cd Python && uv run unreal_mcp_server_advanced.py"
echo ""
echo "🆘 Need help? Check SYSTEM_LAUNCH_GUIDE.md for troubleshooting"
echo "💬 Join our Discord: https://discord.gg/3KNkke3rnH"

# Save process IDs for easy cleanup
{
    echo "# LevlStudio Process IDs - $(date)"
    [ ! -z "$COMFYUI_PID" ] && echo "COMFYUI_PID=$COMFYUI_PID"
    [ ! -z "$MCP_PID" ] && echo "MCP_PID=$MCP_PID"
    [ ! -z "$BLENDER_PID" ] && echo "BLENDER_PID=$BLENDER_PID"
    [ ! -z "$DASHBOARD_PID" ] && echo "DASHBOARD_PID=$DASHBOARD_PID"
} > .levlstudio_pids

echo ""
echo "📋 Process IDs saved to .levlstudio_pids for easy management"