#!/usr/bin/env python3
"""
LevlStudio One-Click Orchestrator
Calls MCP server to execute UE render -> ComfyUI pipeline in one command
"""
import argparse, json, urllib.request, sys, time

def call_mcp_tool(host, port, tool, args):
    """Call a tool on the MCP server via HTTP API"""
    url = f"http://{host}:{port}/tools/call"
    payload = {"name": tool, "arguments": args}
    
    try:
        req = urllib.request.Request(
            url, 
            data=json.dumps(payload).encode("utf-8"), 
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else "Unknown error"
        return {"error": f"HTTP {e.code}: {error_body}"}
    except Exception as e:
        return {"error": f"Request failed: {e}"}

def check_server_status(host, port):
    """Check if MCP server is running"""
    try:
        call_mcp_tool(host, port, "check_status", {})
        return True
    except:
        return False

def main():
    ap = argparse.ArgumentParser(description="LevlStudio One-Click UE5 → ComfyUI Pipeline")
    ap.add_argument("--host", default="127.0.0.1", help="MCP server host")
    ap.add_argument("--port", type=int, default=8765, help="MCP server port")
    
    # UE Parameters
    ap.add_argument("--level", required=True, help="UE Level path (e.g., /Game/Levl/Maps/Empty)")
    ap.add_argument("--bp_path", required=True, help="Blueprint path to spawn (e.g., /Game/Levl/BP/BP_MyCone)")
    ap.add_argument("--movie_out", required=True, help="Output movie path")
    
    # ComfyUI Parameters
    ap.add_argument("--style_img", required=True, help="Style image path for ComfyUI")
    ap.add_argument("--workflow", default="./comfy_workflows/wanfn_depth_pose_canny_template.json", help="ComfyUI workflow JSON")
    ap.add_argument("--output_dir", default="outputs", help="ComfyUI output directory")
    
    # Optional Parameters
    ap.add_argument("--location", default="0,0,300", help="Spawn location (x,y,z)")
    ap.add_argument("--rotation", default="0,0,0", help="Spawn rotation (roll,pitch,yaw)")
    ap.add_argument("--sequence", default="Seq_OneClick", help="Level sequence name")
    ap.add_argument("--resolution", default="1280x720", help="Render resolution")
    ap.add_argument("--fps", type=int, default=24, help="Frame rate")
    ap.add_argument("--poll_timeout", type=int, default=600, help="Max wait time for UE render (seconds)")
    
    # Control flags
    ap.add_argument("--dry_run", action="store_true", help="Show what would be done without executing")
    ap.add_argument("--status_only", action="store_true", help="Check server status and exit")
    
    args = ap.parse_args()

    print("🎬 LevlStudio One-Click Pipeline")
    print("=" * 50)
    
    # Check server status
    print(f"📡 Checking MCP server at {args.host}:{args.port}...")
    if not check_server_status(args.host, args.port):
        print(f"❌ MCP server not accessible at {args.host}:{args.port}")
        print("   Make sure the server is running:")
        print(f"   python3 levl_ue_to_comfy_oneclick_server.py --host {args.host} --port {args.port}")
        sys.exit(1)
    
    print("✅ MCP server is running")
    
    # Get server status details
    status_result = call_mcp_tool(args.host, args.port, "check_status", {})
    if status_result.get("content"):
        status = status_result["content"][0]["text"]
        try:
            status_data = json.loads(status)
            print(f"🔗 UE Bridge: {status_data['ue_bridge']['inbox_count']} inbox, {status_data['ue_bridge']['outbox_count']} outbox")
            print(f"🎨 ComfyUI: {status_data['comfy']['status']}")
        except:
            pass
    
    if args.status_only:
        sys.exit(0)
    
    # Show configuration
    print("\n📋 Configuration:")
    print(f"   Level: {args.level}")
    print(f"   Blueprint: {args.bp_path}")
    print(f"   Spawn Location: {args.location}")
    print(f"   Output Movie: {args.movie_out}")
    print(f"   Style Image: {args.style_img}")
    print(f"   Resolution: {args.resolution} @ {args.fps}fps")
    print(f"   ComfyUI Output: {args.output_dir}")
    
    if args.dry_run:
        print("\n🔍 Dry run mode - no actual execution")
        sys.exit(0)
    
    print("\n🚀 Starting One-Click Pipeline...")
    
    # Execute the one-click tool
    pipeline_args = {
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
        "poll_timeout_sec": args.poll_timeout,
        "output_dir": args.output_dir
    }
    
    print("📤 Submitting to MCP server...")
    result = call_mcp_tool(args.host, args.port, "ue_to_comfy_oneclick", pipeline_args)
    
    if "error" in result:
        print(f"❌ Pipeline failed: {result['error']}")
        sys.exit(1)
    
    # Parse result
    if result.get("content"):
        try:
            content = result["content"][0]["text"]
            data = json.loads(content)
            
            if data.get("ok"):
                print("✅ Pipeline completed successfully!")
                print(f"🎬 UE Movie: {data.get('movie_path', 'N/A')}")
                
                comfy_resp = data.get("comfy_response", {})
                if comfy_resp.get("ok"):
                    print(f"🎨 ComfyUI: Submitted successfully")
                    if comfy_resp.get("response"):
                        try:
                            resp_data = json.loads(comfy_resp["response"])
                            if "prompt_id" in resp_data:
                                print(f"   Prompt ID: {resp_data['prompt_id']}")
                        except:
                            pass
                else:
                    print(f"⚠️ ComfyUI submission failed: {comfy_resp.get('error', 'Unknown error')}")
                
                print(f"\n📁 Check outputs in: {args.output_dir}")
                print("🎉 Done!")
            else:
                print(f"❌ Pipeline failed: {data.get('error', 'Unknown error')}")
                sys.exit(1)
                
        except json.JSONDecodeError:
            print(f"📄 Raw result: {result}")
    else:
        print(f"📄 Unexpected result format: {result}")

if __name__ == "__main__":
    main()
