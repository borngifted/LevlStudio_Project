#!/usr/bin/env python3
"""
LevlStudio One-Click UE5 → ComfyUI MCP Server
Provides tools for end-to-end UE rendering and ComfyUI style transfer
"""
import argparse, json, os, subprocess, uuid, time, pathlib, sys
from typing import Any, Dict, Optional, List

try:
    from mcp.server.fastmcp import FastMCP
except Exception:
    print("Missing MCP server lib. Install with: pip install 'mcp[server]'")
    raise

# ---------------- Bridge queue helpers ----------------
def _ue_paths(root: str):
    base = pathlib.Path(root)
    inbox = base / "inbox"
    outbox = base / "outbox"
    inbox.mkdir(parents=True, exist_ok=True)
    outbox.mkdir(parents=True, exist_ok=True)
    return inbox, outbox

def _ue_enqueue(bridge_root: str, action: str, payload: dict) -> dict:
    """Queue a command for Unreal Engine to process"""
    inbox, _ = _ue_paths(bridge_root)
    cmd_id = f"{int(time.time()*1000)}_{uuid.uuid4().hex[:8]}"
    cmd = {"id": cmd_id, "action": action, "payload": payload, "ts": time.time()}
    path = inbox / f"{cmd_id}.json"
    path.write_text(json.dumps(cmd, indent=2), encoding="utf-8")
    return {"ok": True, "id": cmd_id, "queued": str(path)}

def _ue_fetch(bridge_root: str, cmd_id: str) -> dict:
    """Fetch result from Unreal Engine by command ID"""
    _, outbox = _ue_paths(bridge_root)
    res_path = outbox / f"{cmd_id}.json"
    if not res_path.exists():
        return {"ok": False, "pending": True}
    try:
        return json.loads(res_path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"ok": False, "error": str(e)}

# ---------------- Comfy client helper -----------------
def _submit_to_comfy(host: str, port: int, workflow_path: str, video: str, style: str, out_dir: str) -> dict:
    """Submit workflow to ComfyUI with video and style parameters"""
    import urllib.request
    
    # Load and modify workflow
    wf = json.loads(pathlib.Path(workflow_path).read_text(encoding='utf-8'))
    meta = wf.get("meta", {})
    dyn = meta.get("dynamic_overrides", {})
    
    # Set dynamic parameters
    if video: 
        dyn["video_path"] = video
    if style: 
        dyn["style_image_path"] = style
    if out_dir: 
        dyn["output_dir"] = out_dir
    
    meta["dynamic_overrides"] = dyn
    wf["meta"] = meta
    
    # Submit to ComfyUI
    data = json.dumps(wf).encode('utf-8')
    url = f"http://{host}:{port}/prompt"
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode('utf-8', errors='ignore')
            return {"ok": True, "response": body}
    except Exception as e:
        return {"ok": False, "error": str(e)}

# ---------------- Main ----------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--host', default='127.0.0.1')
    ap.add_argument('--port', type=int, default=8765)
    ap.add_argument('--ue_bridge', default='./UnrealBridge', help='Path to UnrealBridge folder with inbox/outbox')
    ap.add_argument('--comfy_host', default='127.0.0.1')
    ap.add_argument('--comfy_port', type=int, default=8188)
    ap.add_argument('--default_workflow', default='./comfy_workflows/wanfn_depth_pose_canny_template.json')
    args = ap.parse_args()
    
    server = FastMCP('levl-ue-to-comfy')

    # 1) Build + Render (Unreal side, via file-queue to watcher)
    @server.tool()
    def ue_build_and_render(level_path: str = "/Game/Levl/Maps/Empty",
                            bp_path: str = "/Game/Levl/BP/BP_MyCone",
                            spawn_location: str = "0,0,300",
                            spawn_rotation: str = "0,0,0",
                            sequence_name: str = "Seq_OneClick",
                            output_movie_path: str = "",
                            resolution: str = "1280x720",
                            fps: int = 24) -> dict:
        """Requests Unreal to spawn a BP, create a level sequence, add a cine camera, render via MRQ."""
        payload = {
            "level_path": level_path,
            "bp_path": bp_path,
            "spawn_location": spawn_location,
            "spawn_rotation": spawn_rotation,
            "sequence_name": sequence_name,
            "output_movie_path": output_movie_path,
            "resolution": resolution,
            "fps": fps
        }
        return _ue_enqueue(args.ue_bridge, "oneclick_build_and_render", payload)

    # 2) Poll Unreal result by cmd_id
    @server.tool()
    def ue_fetch_result(cmd_id: str) -> dict:
        """Fetch result from Unreal Engine by command ID"""
        return _ue_fetch(args.ue_bridge, cmd_id)

    # 3) Submit video to ComfyUI
    @server.tool()
    def comfy_submit_video(video_path: str,
                           style_image_path: str,
                           workflow_path: str = "",
                           output_dir: str = "outputs") -> dict:
        """Submit video to ComfyUI for style transfer"""
        wf_path = workflow_path or args.default_workflow
        return _submit_to_comfy(args.comfy_host, args.comfy_port, wf_path, video_path, style_image_path, output_dir)

    # 4) One-click: build+render in UE, then submit to Comfy when done
    @server.tool()
    def ue_to_comfy_oneclick(level_path: str,
                             bp_path: str,
                             output_movie_path: str,
                             style_image_path: str,
                             comfy_workflow: str = "",
                             spawn_location: str = "0,0,300",
                             spawn_rotation: str = "0,0,0",
                             sequence_name: str = "Seq_OneClick",
                             resolution: str = "1280x720",
                             fps: int = 24,
                             poll_seconds: int = 2,
                             poll_timeout_sec: int = 600,
                             output_dir: str = "outputs") -> dict:
        """End-to-end: ask UE to render, wait, then push video to ComfyUI workflow."""
        
        # Step 1: Enqueue UE job
        payload = {
            "level_path": level_path, 
            "bp_path": bp_path,
            "spawn_location": spawn_location, 
            "spawn_rotation": spawn_rotation,
            "sequence_name": sequence_name, 
            "output_movie_path": output_movie_path,
            "resolution": resolution, 
            "fps": fps
        }
        enq = _ue_enqueue(args.ue_bridge, "oneclick_build_and_render", payload)
        cmd_id = enq["id"]
        
        print(f"Queued UE render job: {cmd_id}")
        
        # Step 2: Poll for completion
        start = time.time()
        result_path = ""
        while True:
            res = _ue_fetch(args.ue_bridge, cmd_id)
            if res.get("ok") and res.get("data", {}).get("movie_path"):
                result_path = res["data"]["movie_path"]
                print(f"UE render completed: {result_path}")
                break
            if res.get("ok") == False and not res.get("pending"):
                return {"ok": False, "error": f"UE render failed: {res.get('error')}", "cmd_id": cmd_id}
            if time.time() - start > poll_timeout_sec:
                return {"ok": False, "error": "UE render timed out", "cmd_id": cmd_id}
            print(f"Waiting for UE render... ({int(time.time() - start)}s)")
            time.sleep(poll_seconds)
        
        # Step 3: Submit to ComfyUI
        wf = comfy_workflow or args.default_workflow
        try:
            print(f"Submitting to ComfyUI: {result_path} + {style_image_path}")
            resp = _submit_to_comfy(args.comfy_host, args.comfy_port, wf, result_path, style_image_path, output_dir)
            if resp.get("ok"):
                print("ComfyUI submission successful")
                return {"ok": True, "movie_path": result_path, "comfy_response": resp}
            else:
                return {"ok": False, "error": f"ComfyUI failed: {resp.get('error')}", "movie_path": result_path}
        except Exception as e:
            return {"ok": False, "error": f"Comfy submission failed: {e}", "movie_path": result_path}

    # 5) Check system status
    @server.tool()
    def check_status() -> dict:
        """Check status of UE bridge and ComfyUI"""
        import urllib.request
        
        # Check UE bridge
        inbox, outbox = _ue_paths(args.ue_bridge)
        inbox_count = len(list(inbox.glob("*.json")))
        outbox_count = len(list(outbox.glob("*.json")))
        
        # Check ComfyUI
        comfy_ok = False
        try:
            url = f"http://{args.comfy_host}:{args.comfy_port}/system_stats"
            with urllib.request.urlopen(url, timeout=5) as resp:
                comfy_ok = resp.status == 200
        except:
            pass
        
        return {
            "ok": True,
            "ue_bridge": {
                "inbox_path": str(inbox),
                "outbox_path": str(outbox),
                "inbox_count": inbox_count,
                "outbox_count": outbox_count
            },
            "comfy": {
                "host": args.comfy_host,
                "port": args.comfy_port,
                "status": "running" if comfy_ok else "not accessible"
            },
            "workflow": args.default_workflow
        }

    # Run server
    print(f"🎬 LevlStudio UE→ComfyUI MCP Server")
    print(f"📡 Listening on {args.host}:{args.port}")
    print(f"🔗 UE Bridge: {args.ue_bridge}")
    print(f"🎨 ComfyUI: {args.comfy_host}:{args.comfy_port}")
    print(f"⚙️  Default workflow: {args.default_workflow}")
    print("")
    print("Available tools:")
    print("  - ue_build_and_render: Queue UE render job")
    print("  - ue_fetch_result: Check UE job status")
    print("  - comfy_submit_video: Submit video to ComfyUI")
    print("  - ue_to_comfy_oneclick: End-to-end pipeline")
    print("  - check_status: System status check")
    print("")
    
    server.run()

if __name__ == '__main__':
    main()