@echo off
REM Interactive WAN Video Workflow Launcher for Windows
REM Provides menu-driven interface for launching different workflows

setlocal enabledelayedexpansion

:main_menu
cls
echo.
echo ========================================
echo   LevlStudio WAN Video Workflows
echo ========================================
echo.
echo  1. WAN VACE (Reference-to-Video)
echo  2. WAN I2V (Image-to-Video GGUF + LoRA)
echo  3. View Running Services
echo  4. Open ComfyUI Interface
echo  5. Exit
echo.
set /p choice="Select an option (1-5): "

if "!choice!"=="1" goto launch_vace
if "!choice!"=="2" goto launch_i2v
if "!choice!"=="3" goto view_services
if "!choice!"=="4" goto open_comfyui
if "!choice!"=="5" goto exit
goto main_menu

:launch_vace
cls
echo.
echo ========================================
echo   Launching WAN VACE Workflow
echo ========================================
echo.
call "%~dp0launch_vace.bat"
pause
goto main_menu

:launch_i2v
cls
echo.
echo ========================================
echo   Launching WAN I2V Workflow
echo ========================================
echo.
call "%~dp0launch_i2v.bat"
pause
goto main_menu

:view_services
cls
echo.
echo ========================================
echo   Service Status Check
echo ========================================
echo.
echo Checking ComfyUI (Port 8188)...
curl -s http://127.0.0.1:8188 >nul 2>&1
if !errorlevel! equ 0 (
    echo   ComfyUI: RUNNING
    echo   URL: http://127.0.0.1:8188
) else (
    echo   ComfyUI: NOT RUNNING
)

echo.
echo Checking Model Router (Port 3000)...
curl -s http://localhost:3000 >nul 2>&1
if !errorlevel! equ 0 (
    echo   Model Router: RUNNING
    echo   URL: http://localhost:3000
) else (
    echo   Model Router: NOT RUNNING
)

echo.
echo Available Workflows:
echo   - wanvideo_1_3B_VACE_MDMZ.json
echo   - goshniiAI-WAN 2.2 Image-to-Video l GGUF + LoRA.json
echo.
pause
goto main_menu

:open_comfyui
echo.
echo Opening ComfyUI interface...
start http://127.0.0.1:8188
goto main_menu

:exit
echo.
echo Goodbye!
endlocal
exit /b 0