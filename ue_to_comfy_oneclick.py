#!/usr/bin/env python3
"""
LevlStudio UE to ComfyUI One-Click Orchestrator
Calls MCP server to do UE render -> Comfy submit in one go
"""

import argparse, json, urllib.request

def call_tool(host, port, tool, args):
    """Call an MCP tool via HTTP"""
    url = f"http://{host}:{port}/tools/run"
    payload = {"tool": tool, "args": args}
    req = urllib.request.Request(
        url, 
        data=json.dumps(payload).encode("utf-8"), 
        headers={"Content-Type":"application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def main():
    ap = argparse.ArgumentParser(description="LevlStudio One-Click: UE5 render → ComfyUI style transfer")
    ap.add_argument("--host", default="127.0.0.1", help="MCP server host")
    ap.add_argument("--port", type=int, default=8765, help="MCP server port")
    ap.add_argument("--level", required=True, help="UE level path (e.g., /Game/Levl/Maps/Empty)")
    ap.add_argument("--bp_path", required=True, help="Blueprint to spawn (e.g., /Game/Levl/BP/BP_MyCone)")
    ap.add_argument("--movie_out", required=True, help="Output movie path")
    ap.add_argument("--style_img", required=True, help="Style image for ComfyUI")
    ap.add_argument("--workflow", default="./comfy_workflows/wanfn_depth_pose_canny_template.json", 
                   help="ComfyUI workflow JSON")
    ap.add_argument("--location", default="0,0,300", help="Spawn location (X,Y,Z)")
    ap.add_argument("--rotation", default="0,0,0", help="Spawn rotation (Roll,Pitch,Yaw)")
    ap.add_argument("--sequence", default="Seq_OneClick", help="Level sequence name")
    ap.add_argument("--resolution", default="1280x720", help="Render resolution")
    ap.add_argument("--fps", type=int, default=24, help="Frames per second")
    ap.add_argument("--output_dir", default="outputs", help="ComfyUI output directory")
    ap.add_argument("--poll_timeout", type=int, default=600, help="Max seconds to wait for UE render")
    
    args = ap.parse_args()

    print("🎬 LevlStudio One-Click Pipeline")
    print("=" * 50)
    print(f"Level: {args.level}")
    print(f"Blueprint: {args.bp_path}")
    print(f"Style: {args.style_img}")
    print(f"Resolution: {args.resolution} @ {args.fps}fps")
    print("")

    print("📡 Calling MCP server...")
    res = call_tool(args.host, args.port, "ue_to_comfy_oneclick", {
        "level_path": args.level,
        "bp_path": args.bp_path,
        "output_movie_path": args.movie_out,
        "style_image_path": args.style_img,
        "comfy_workflow": args.workflow,
        "spawn_location": args.location,
        "spawn_rotation": args.rotation,
        "sequence_name": args.sequence,
        "resolution": args.resolution,
        "fps": args.fps,
        "output_dir": args.output_dir,
        "poll_timeout_sec": args.poll_timeout
    })
    
    print("")
    if res.get("ok"):
        print("✅ Success!")
        print(f"   Movie: {res.get('movie_path')}")
        if res.get('comfy_response'):
            print(f"   ComfyUI: Job submitted")
        print(f"   Output will appear in: {args.output_dir}/")
    else:
        print("❌ Failed!")
        print(f"   Error: {res.get('error')}")
        if res.get('movie_path'):
            print(f"   Partial result: {res.get('movie_path')}")
    
    print("")
    print("Full response:")
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
