#!/bin/bash
# WAN VACE (Reference-to-Video) Workflow Launcher for macOS
# Launches ComfyUI and executes the VACE workflow with interactive input

set -e

echo ""
echo "================================"
echo "  WAN VACE Workflow Launcher"
echo "================================"
echo ""

# Set project paths
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

# Function to check if ComfyUI is running
check_comfyui() {
    curl -s http://127.0.0.1:8188 >/dev/null 2>&1
}

# Check if ComfyUI is running
echo "Checking ComfyUI status..."
if ! check_comfyui; then
    echo "Starting ComfyUI..."
    python3 ComfyUI/main.py --port 8188 &
    COMFYUI_PID=$!
    
    echo "Waiting for ComfyUI to start..."
    for i in {1..30}; do
        if check_comfyui; then
            echo "ComfyUI is ready!"
            break
        fi
        sleep 2
        if [ $i -eq 30 ]; then
            echo "ERROR: ComfyUI failed to start"
            exit 1
        fi
    done
else
    echo "ComfyUI is already running."
fi

echo ""
echo "================================"
echo "  Workflow Input Configuration"
echo "================================"
echo ""

# Get input paths from user
read -p "Enter path to input video (or press Enter for example): " input_video
input_video=${input_video:-"examples/input_video.mp4"}

read -p "Enter path to reference image (or press Enter for example): " ref_image
ref_image=${ref_image:-"examples/reference.jpg"}

read -p "Enter output directory (or press Enter for default): " output_dir
output_dir=${output_dir:-"ComfyUI/output/vace"}

# Create output directory if it doesn't exist
mkdir -p "$output_dir"

echo ""
echo "Input Video: $input_video"
echo "Reference Image: $ref_image"
echo "Output Directory: $output_dir"
echo ""

# Set environment variables for levl_enqueue.py
export LEVL_INPUT_DIR="$input_video"
export LEVL_REF_IMAGE="$ref_image"
export LEVL_OUTPUT_DIR="$output_dir"

echo "Launching VACE workflow..."
if python3 tools/levl_enqueue.py --workflow "ComfyUI/workflow_results/wanvideo_1_3B_VACE_MDMZ.json" --host 127.0.0.1 --port 8188; then
    echo ""
    echo "================================"
    echo "  Workflow Submitted Successfully"
    echo "================================"
    echo ""
    echo "Monitor progress at: http://127.0.0.1:8188"
    echo "Output will be saved to: $output_dir"
    echo ""
    echo "Press Enter to open ComfyUI in browser..."
    read -r
    open http://127.0.0.1:8188
else
    echo ""
    echo "ERROR: Failed to submit workflow"
    echo "Check the console output above for details"
    echo ""
    read -p "Press Enter to exit..."
fi