#!/bin/bash
# Interactive WAN Video Workflow Launcher for macOS
# Provides menu-driven interface for launching different workflows

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to check service status
check_service() {
    local url=$1
    curl -s "$url" >/dev/null 2>&1
}

# Function to display main menu
show_main_menu() {
    clear
    echo ""
    echo "========================================"
    echo "   LevlStudio WAN Video Workflows"
    echo "========================================"
    echo ""
    echo "  1. WAN VACE (Reference-to-Video)"
    echo "  2. WAN I2V (Image-to-Video GGUF + LoRA)"
    echo "  3. View Running Services"
    echo "  4. Open ComfyUI Interface"
    echo "  5. Exit"
    echo ""
    read -p "Select an option (1-5): " choice
}

# Function to launch VACE workflow
launch_vace() {
    clear
    echo ""
    echo "========================================"
    echo "   Launching WAN VACE Workflow"
    echo "========================================"
    echo ""
    bash "$SCRIPT_DIR/launch_vace.sh"
    read -p "Press Enter to continue..."
}

# Function to launch I2V workflow
launch_i2v() {
    clear
    echo ""
    echo "========================================"
    echo "   Launching WAN I2V Workflow"
    echo "========================================"
    echo ""
    bash "$SCRIPT_DIR/launch_i2v.sh"
    read -p "Press Enter to continue..."
}

# Function to view running services
view_services() {
    clear
    echo ""
    echo "========================================"
    echo "   Service Status Check"
    echo "========================================"
    echo ""
    
    echo "Checking ComfyUI (Port 8188)..."
    if check_service "http://127.0.0.1:8188"; then
        echo "  ComfyUI: RUNNING"
        echo "  URL: http://127.0.0.1:8188"
    else
        echo "  ComfyUI: NOT RUNNING"
    fi
    
    echo ""
    echo "Checking Model Router (Port 3000)..."
    if check_service "http://localhost:3000"; then
        echo "  Model Router: RUNNING"
        echo "  URL: http://localhost:3000"
    else
        echo "  Model Router: NOT RUNNING"
    fi
    
    echo ""
    echo "Available Workflows:"
    echo "  - wanvideo_1_3B_VACE_MDMZ.json"
    echo "  - goshniiAI-WAN 2.2 Image-to-Video l GGUF + LoRA.json"
    echo ""
    read -p "Press Enter to continue..."
}

# Function to open ComfyUI
open_comfyui() {
    echo ""
    echo "Opening ComfyUI interface..."
    open http://127.0.0.1:8188
}

# Main loop
while true; do
    show_main_menu
    
    case $choice in
        1)
            launch_vace
            ;;
        2)
            launch_i2v
            ;;
        3)
            view_services
            ;;
        4)
            open_comfyui
            ;;
        5)
            echo ""
            echo "Goodbye!"
            exit 0
            ;;
        *)
            echo "Invalid option. Please try again."
            sleep 2
            ;;
    esac
done