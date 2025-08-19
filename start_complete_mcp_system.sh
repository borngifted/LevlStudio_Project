#!/bin/bash
# Complete LevlStudio + Unreal MCP System Launcher
# This script launches all services for the complete AI-to-3D pipeline

echo "🚀 Launching Complete LevlStudio + Unreal MCP System..."

PROJECT_ROOT="/Volumes/Jul_23_2025/LevlStudio_Project"
cd "$PROJECT_ROOT"

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

echo "🔧 Starting Core Services..."

# 1. ComfyUI Server
echo "📊 Checking ComfyUI..."
if check_port 8199; then
    echo "✅ ComfyUI already running on port 8199"
else
    if [ -d "ComfyUI/ComfyUI" ]; then
        echo "Starting ComfyUI..."
        cd ComfyUI/ComfyUI
        if [ -d "venv" ]; then
            source venv/bin/activate
        fi
        python main.py --port 8199 > "$PROJECT_ROOT/logs/comfyui.log" 2>&1 &
        COMFYUI_PID=$!
        cd "$PROJECT_ROOT"
        
        if wait_for_service "http://127.0.0.1:8199/queue" 30; then
            echo "✅ ComfyUI started (PID: $COMFYUI_PID)"
        fi
    fi
fi

# 2. MCP Filesystem Server
echo "📁 Checking MCP Filesystem Server..."
if ! ps aux | grep "mcp-server-filesystem" | grep -v grep > /dev/null; then
    echo "Starting MCP Filesystem Server..."
    npx @modelcontextprotocol/server-filesystem "$PROJECT_ROOT" > "$PROJECT_ROOT/logs/mcp_filesystem.log" 2>&1 &
    MCP_FS_PID=$!
    sleep 3
    echo "✅ MCP Filesystem Server started (PID: $MCP_FS_PID)"
fi

# 3. Blender with LevlStudio addon
echo "🎨 Checking Blender LevlStudio addon..."
if ! ps aux | grep "levlstudio_scene_builder_addon.py" | grep -v grep > /dev/null; then
    if [ -f "levlstudio_scene_builder_addon.py" ]; then
        echo "Starting Blender with LevlStudio addon..."
        /Applications/Blender.app/Contents/MacOS/Blender --python levlstudio_scene_builder_addon.py > "$PROJECT_ROOT/logs/blender.log" 2>&1 &
        BLENDER_PID=$!
        sleep 5
        echo "✅ Blender started with LevlStudio addon (PID: $BLENDER_PID)"
    fi
fi

# 4. LevlStudio MCP Server
echo "🏗️  Starting LevlStudio MCP Server..."
if [ -f "levl_mcp_server.py" ]; then
    python levl_mcp_server.py > "$PROJECT_ROOT/logs/levl_mcp_server.log" 2>&1 &
    LEVL_MCP_PID=$!
    sleep 3
    echo "✅ LevlStudio MCP Server started (PID: $LEVL_MCP_PID)"
fi

# 4b. Model Router MCP Server
echo "🧠 Starting Model Router MCP Server..."
if [ -f "model_router_mcp_server.py" ]; then
    python model_router_mcp_server.py > "$PROJECT_ROOT/logs/model_router_mcp.log" 2>&1 &
    MODEL_ROUTER_MCP_PID=$!
    sleep 3
    echo "✅ Model Router MCP Server started (PID: $MODEL_ROUTER_MCP_PID)"
fi

# 5. Model Router Backend Service
echo "🤖 Starting Model Router Backend Service..."
if [ -d "model router" ]; then
    cd "model router"
    # Check if npm dependencies are installed
    if [ ! -d "node_modules" ]; then
        echo "Installing Model Router dependencies..."
        npm install
    fi
    # Start the model router dashboard server
    node dashboard-server.mjs > "$PROJECT_ROOT/logs/model_router.log" 2>&1 &
    MODEL_ROUTER_PID=$!
    cd "$PROJECT_ROOT"
    sleep 3
    echo "✅ Model Router Backend Service started (PID: $MODEL_ROUTER_PID)"
    echo "   📊 Dashboard available at: http://localhost:3000"
fi

# 6. Unreal Engine MCP Server
echo "🎮 Starting Unreal Engine MCP Server..."
if [ -d "Python_UnrealMCP" ]; then
    cd Python_UnrealMCP
    uv run unreal_mcp_server_advanced.py > "$PROJECT_ROOT/logs/unreal_mcp_server.log" 2>&1 &
    UNREAL_MCP_PID=$!
    cd "$PROJECT_ROOT"
    sleep 3
    echo "✅ Unreal Engine MCP Server started (PID: $UNREAL_MCP_PID)"
fi

echo ""
echo "🔍 System Health Check:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Health checks
if curl -s http://127.0.0.1:8199/queue > /dev/null 2>&1; then
    echo "✅ ComfyUI: Running and ready (port 8199)"
else
    echo "❌ ComfyUI: Not responding"
fi

if ps aux | grep "mcp-server-filesystem" | grep -v grep > /dev/null; then
    echo "✅ MCP Filesystem: Running"
else
    echo "❌ MCP Filesystem: Not running"
fi

if ps aux | grep "levlstudio_scene_builder_addon" | grep -v grep > /dev/null; then
    echo "✅ Blender LevlStudio: Running"
else
    echo "❌ Blender LevlStudio: Not running"
fi

if ps aux | grep "levl_mcp_server.py" | grep -v grep > /dev/null; then
    echo "✅ LevlStudio MCP: Running"
else
    echo "❌ LevlStudio MCP: Not running"
fi

if ps aux | grep "model_router_mcp_server.py" | grep -v grep > /dev/null; then
    echo "✅ Model Router MCP: Running"
else
    echo "❌ Model Router MCP: Not running"
fi

if ps aux | grep "dashboard-server.mjs" | grep -v grep > /dev/null; then
    echo "✅ Model Router: Running"
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "   📊 Dashboard accessible at http://localhost:3000"
    fi
else
    echo "❌ Model Router: Not running"
fi

if ps aux | grep "unreal_mcp_server_advanced.py" | grep -v grep > /dev/null; then
    echo "✅ Unreal MCP: Running"
else
    echo "❌ Unreal MCP: Not running"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Save process IDs
{
    echo "# Complete MCP System Process IDs - $(date)"
    [ ! -z "$COMFYUI_PID" ] && echo "COMFYUI_PID=$COMFYUI_PID"
    [ ! -z "$MCP_FS_PID" ] && echo "MCP_FS_PID=$MCP_FS_PID"
    [ ! -z "$BLENDER_PID" ] && echo "BLENDER_PID=$BLENDER_PID"
    [ ! -z "$LEVL_MCP_PID" ] && echo "LEVL_MCP_PID=$LEVL_MCP_PID"
    [ ! -z "$MODEL_ROUTER_MCP_PID" ] && echo "MODEL_ROUTER_MCP_PID=$MODEL_ROUTER_MCP_PID"
    [ ! -z "$MODEL_ROUTER_PID" ] && echo "MODEL_ROUTER_PID=$MODEL_ROUTER_PID"
    [ ! -z "$UNREAL_MCP_PID" ] && echo "UNREAL_MCP_PID=$UNREAL_MCP_PID"
} > .complete_system_pids

echo ""
echo "🎯 Complete LevlStudio + Unreal MCP System Ready!"
echo ""
echo "📝 Next Steps:"
echo "   1. Copy mcp_config_complete.json to your MCP client config"
echo "   2. Open Unreal Engine project with UnrealMCP plugin"
echo "   3. Start creating with AI-to-3D pipeline!"
echo ""
echo "📊 Monitor logs in: $PROJECT_ROOT/logs/"
echo "🛑 Stop system: ./stop_complete_mcp_system.sh"