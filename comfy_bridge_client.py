#!/usr/bin/env python3
"""
comfy_bridge_client.py
Submits a ComfyUI prompt/workflow to the HTTP API.

Usage:
  python3 comfy_bridge_client.py \
    --host 127.0.0.1 --port 8188 \
    --workflow comfy_workflows/wanfn_depth_pose_canny_template.json \
    --video_in exports/ue_shot01.mp4 \
    --style_img refs/style_look1.png \
    --out_dir outputs
"""
import argparse, json, sys, urllib.request

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--host', default='127.0.0.1')
    ap.add_argument('--port', type=int, default=8188)
    ap.add_argument('--workflow', required=True)
    ap.add_argument('--video_in', default='')
    ap.add_argument('--style_img', default='')
    ap.add_argument('--out_dir', default='outputs')
    args = ap.parse_args()

    with open(args.workflow, 'r', encoding='utf-8') as f:
        wf = json.load(f)

    # Expecting the JSON you saved earlier with meta.dynamic_overrides + prompt graph.
    # If you used the simple “workflow” format instead, adapt this section accordingly.
    meta = wf.get("meta", {})
    dyn = meta.get("dynamic_overrides", {})
    if args.video_in:
        dyn["video_path"] = args.video_in
    if args.style_img:
        dyn["style_image_path"] = args.style_img
    if args.out_dir:
        dyn["output_dir"] = args.out_dir
    meta["dynamic_overrides"] = dyn
    wf["meta"] = meta

    data = json.dumps(wf).encode('utf-8')
    url = f"http://{args.host}:{args.port}/prompt"

    try:
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as resp:
            print(resp.read().decode('utf-8', errors='ignore'))
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
