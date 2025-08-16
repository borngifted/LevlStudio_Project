
LevlStudio Controller Package — Quick Start
==========================================

1) Copy all files to your project folder, e.g.:
   /Users/workofficial/Desktop/The_13th_Night/LevlStudio_Project

2) Create venv and install MCP server:
   python3 -m venv .venv
   source .venv/bin/activate
   python3 -m pip install --upgrade pip "mcp[server]"
   # optional for LLM troubleshoot
   python3 -m pip install openai google-generativeai

3) Start server:
   python3 levl_mcp_server.py      --blender "/Applications/Blender.app/Contents/MacOS/Blender"      --addon   "./levlstudio_scene_builder_addon.py"      --assets  "./json/assets.json"      --scenes  "./json/scenes.json"      --project "."

4) VS Code tasks:
   mkdir -p .vscode && cp vscode_tasks_examples/tasks.json .vscode/tasks.json
   - Run task: "Levl: Build Scene (CLI)"

5) MCP tools available:
   - load_json_and_list_scenes
   - build_scene
   - resolve_report
   - troubleshoot_scene

Note: The add-on uses env vars OPENAI_API_KEY and GOOGLE_API_KEY for AI.
