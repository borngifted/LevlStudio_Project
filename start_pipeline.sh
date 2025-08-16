#!/bin/bash
# LevlStudio One-Click Pipeline - Quick Start Script

echo "🎬 LevlStudio UE5 → ComfyUI Pipeline"
echo "====================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Project directory
PROJECT_DIR="/Users/workofficial/Desktop/The_13th_Night/LevlStudio_Project"
cd "$PROJECT_DIR"

# Function to check if a process is running
check_process() {
    if lsof -i:$1 > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Main menu
show_menu() {
    echo "What would you like to do?"
    echo ""
    echo "1) Start MCP Server (UE→Comfy Bridge)"
    echo "2) Start ComfyUI"
    echo "3) Run One-Click Pipeline"
    echo "4) Install Dependencies"
    echo "5) Test Bridge Connection"
    echo "6) Clear Bridge Queue"
    echo "7) Open VS Code"
    echo "8) Check System Status"
    echo "0) Exit"
    echo ""
    read -p "Enter choice [0-8]: " choice
}

# Start MCP Server
start_mcp() {
    echo -e "${YELLOW}Starting MCP Server...${NC}"
    
    if check_process 8765; then
        echo -e "${YELLOW}MCP Server already running on port 8765${NC}"
        return
    fi
    
    # Create new terminal window for MCP server
    osascript -e "
    tell application \"Terminal\"
        do script \"cd '$PROJECT_DIR' && source .venv/bin/activate && export UE_BRIDGE='./UnrealBridge' && export COMFY_HOST='127.0.0.1' && export COMFY_PORT='8188' && python3 levl_ue_to_comfy_server.py --ue_bridge './UnrealBridge'\"
    end tell"
    
    echo -e "${GREEN}✓ MCP Server starting in new terminal${NC}"
    sleep 2
}

# Start ComfyUI
start_comfy() {
    echo -e "${YELLOW}Starting ComfyUI...${NC}"
    
    if check_process 8188; then
        echo -e "${YELLOW}ComfyUI already running on port 8188${NC}"
        return
    fi
    
    # Adjust path to your ComfyUI installation
    COMFY_PATH="$HOME/ComfyUI"
    
    if [ ! -d "$COMFY_PATH" ]; then
        echo -e "${RED}ComfyUI not found at: $COMFY_PATH${NC}"
        echo "Please update COMFY_PATH in this script"
        return
    fi
    
    osascript -e "
    tell application \"Terminal\"
        do script \"cd '$COMFY_PATH' && python main.py --listen 127.0.0.1 --port 8188\"
    end tell"
    
    echo -e "${GREEN}✓ ComfyUI starting in new terminal${NC}"
    sleep 2
}

# Run pipeline
run_pipeline() {
    echo -e "${YELLOW}Running One-Click Pipeline...${NC}"
    echo ""
    
    # Check if MCP server is running
    if ! check_process 8765; then
        echo -e "${RED}Error: MCP Server not running. Start it first (option 1)${NC}"
        return
    fi
    
    # Get parameters
    read -p "UE Level path [/Game/Levl/Maps/Empty]: " level
    level=${level:-/Game/Levl/Maps/Empty}
    
    read -p "Blueprint path [/Game/The13thNight/BP/BP_Nimble]: " bp
    bp=${bp:-/Game/The13thNight/BP/BP_Nimble}
    
    echo "Available styles:"
    echo "1) festive_night"
    echo "2) ice_crystal"
    echo "3) magical_glow"
    echo "4) dark_forest"
    echo "5) candy_cane"
    read -p "Choose style [1]: " style_choice
    
    case $style_choice in
        2) style="ice_crystal";;
        3) style="magical_glow";;
        4) style="dark_forest";;
        5) style="candy_cane";;
        *) style="festive_night";;
    esac
    
    # Run the pipeline
    python3 ue_to_comfy_oneclick.py \
        --level "$level" \
        --bp_path "$bp" \
        --movie_out "./exports/oneclick_$(date +%Y%m%d_%H%M%S).mp4" \
        --style_img "./refs/style_${style}.png" \
        --workflow "./comfy_workflows/wanfn_depth_pose_canny_template.json" \
        --location "0,0,100" \
        --rotation "0,0,0" \
        --resolution "1280x720" \
        --fps 24 \
        --output_dir "./outputs"
    
    echo ""
    echo -e "${YELLOW}Remember to click 'Levl Bridge: Run Once' in Unreal Engine!${NC}"
}

# Install dependencies
install_deps() {
    echo -e "${YELLOW}Installing dependencies...${NC}"
    
    # Create venv if not exists
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
    fi
    
    source .venv/bin/activate
    pip install --upgrade pip
    pip install 'mcp[server]' fastmcp
    
    echo -e "${GREEN}✓ Dependencies installed${NC}"
}

# Test bridge
test_bridge() {
    echo -e "${YELLOW}Testing bridge connection...${NC}"
    
    # Create test command
    python3 -c "
import json, time
path = './UnrealBridge/inbox/test_' + str(int(time.time())) + '.json'
data = {'id': 'test', 'action': 'ping', 'payload': {}}
with open(path, 'w') as f:
    json.dump(data, f)
print(f'Test command written to: {path}')
"
    
    echo -e "${GREEN}✓ Test command sent to bridge${NC}"
    echo "Check Unreal Engine and run 'Levl Bridge: Run Once' to process"
}

# Clear queue
clear_queue() {
    echo -e "${YELLOW}Clearing bridge queue...${NC}"
    
    rm -f ./UnrealBridge/inbox/*.json 2>/dev/null
    rm -f ./UnrealBridge/outbox/*.json 2>/dev/null
    
    echo -e "${GREEN}✓ Queue cleared${NC}"
}

# Open VS Code
open_vscode() {
    if command -v code &> /dev/null; then
        code .
        echo -e "${GREEN}✓ VS Code opened${NC}"
    else
        echo -e "${RED}VS Code command not found. Install from: https://code.visualstudio.com/${NC}"
    fi
}

# Check status
check_status() {
    echo -e "${YELLOW}System Status:${NC}"
    echo ""
    
    # MCP Server
    if check_process 8765; then
        echo -e "MCP Server:  ${GREEN}● Running${NC} (port 8765)"
    else
        echo -e "MCP Server:  ${RED}○ Not running${NC}"
    fi
    
    # ComfyUI
    if check_process 8188; then
        echo -e "ComfyUI:     ${GREEN}● Running${NC} (port 8188)"
    else
        echo -e "ComfyUI:     ${RED}○ Not running${NC}"
    fi
    
    # Check bridge folders
    if [ -d "./UnrealBridge/inbox" ] && [ -d "./UnrealBridge/outbox" ]; then
        inbox_count=$(ls -1 ./UnrealBridge/inbox/*.json 2>/dev/null | wc -l)
        outbox_count=$(ls -1 ./UnrealBridge/outbox/*.json 2>/dev/null | wc -l)
        echo -e "Bridge:      ${GREEN}● Ready${NC} (Inbox: $inbox_count, Outbox: $outbox_count)"
    else
        echo -e "Bridge:      ${RED}○ Not configured${NC}"
    fi
    
    # Check exports
    if [ -d "./exports" ]; then
        export_count=$(ls -1 ./exports/*.mp4 2>/dev/null | wc -l)
        echo -e "Exports:     $export_count videos"
    fi
    
    # Check outputs
    if [ -d "./outputs" ]; then
        output_count=$(ls -1 ./outputs/*.mp4 2>/dev/null | wc -l)
        echo -e "Outputs:     $output_count styled videos"
    fi
}

# Main loop
while true; do
    echo ""
    show_menu
    
    case $choice in
        1) start_mcp ;;
        2) start_comfy ;;
        3) run_pipeline ;;
        4) install_deps ;;
        5) test_bridge ;;
        6) clear_queue ;;
        7) open_vscode ;;
        8) check_status ;;
        0) echo "Goodbye!"; exit 0 ;;
        *) echo -e "${RED}Invalid option${NC}" ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
done
