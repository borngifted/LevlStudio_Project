@echo off
REM WAN VACE (Reference-to-Video) Workflow Launcher for Windows
REM Launches ComfyUI and executes the VACE workflow with interactive input

setlocal enabledelayedexpansion

echo.
echo ================================
echo  WAN VACE Workflow Launcher
echo ================================
echo.

REM Set project paths
set PROJECT_ROOT=%~dp0..\..
cd /d "%PROJECT_ROOT%"

REM Check if ComfyUI is running
echo Checking ComfyUI status...
curl -s http://127.0.0.1:8188 >nul 2>&1
if !errorlevel! neq 0 (
    echo Starting ComfyUI...
    start /b python ComfyUI\main.py --port 8188
    
    echo Waiting for ComfyUI to start...
    :wait_loop
    timeout /t 2 /nobreak >nul
    curl -s http://127.0.0.1:8188 >nul 2>&1
    if !errorlevel! neq 0 goto wait_loop
    
    echo ComfyUI is ready!
) else (
    echo ComfyUI is already running.
)

echo.
echo ================================
echo  Workflow Input Configuration
echo ================================
echo.

REM Get input paths from user
set /p input_video="Enter path to input video (or press Enter for example): "
if "!input_video!"=="" set input_video=examples\input_video.mp4

set /p ref_image="Enter path to reference image (or press Enter for example): "
if "!ref_image!"=="" set ref_image=examples\reference.jpg

set /p output_dir="Enter output directory (or press Enter for default): "
if "!output_dir!"=="" set output_dir=ComfyUI\output\vace

REM Create output directory if it doesn't exist
if not exist "!output_dir!" mkdir "!output_dir!"

echo.
echo Input Video: !input_video!
echo Reference Image: !ref_image!
echo Output Directory: !output_dir!
echo.

REM Set environment variables for levl_enqueue.py
set LEVL_INPUT_DIR=!input_video!
set LEVL_REF_IMAGE=!ref_image!
set LEVL_OUTPUT_DIR=!output_dir!

echo Launching VACE workflow...
python tools\levl_enqueue.py --workflow "ComfyUI\workflow_results\wanvideo_1_3B_VACE_MDMZ.json" --host 127.0.0.1 --port 8188

if !errorlevel! equ 0 (
    echo.
    echo ================================
    echo  Workflow Submitted Successfully
    echo ================================
    echo.
    echo Monitor progress at: http://127.0.0.1:8188
    echo Output will be saved to: !output_dir!
    echo.
    echo Press any key to open ComfyUI in browser...
    pause >nul
    start http://127.0.0.1:8188
) else (
    echo.
    echo ERROR: Failed to submit workflow
    echo Check the console output above for details
    echo.
    pause
)

endlocal