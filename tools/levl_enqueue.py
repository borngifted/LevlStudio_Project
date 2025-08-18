#!/usr/bin/env python3
"""
levl_enqueue.py
Posts a ComfyUI workflow JSON to the /prompt API, with optional simple overrides via env vars:
  LEVL_INPUT_DIR   - path to frames folder or input video (string searched into nodes)
  LEVL_REF_IMAGE   - path to reference image (string searched into nodes)
  LEVL_OUTPUT_DIR  - output frames folder (string searched into nodes)

Usage:
  python tools/levl_enqueue.py --workflow "ComfyUI/workflow_results/wanvideo_1_3B_VACE_MDMZ.json" --host 127.0.0.1 --port 8188
"""
import os, sys, json, time, uuid
import argparse
from urllib import request, error

def _http_post(url: str, data: dict, timeout=20):
    body = json.dumps(data).encode("utf-8")
    req = request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))

def _wait_for_server(host, port, retries=60, delay=1.0):
    url = f"http://{host}:{port}/object_info"
    for _ in range(retries):
        try:
            with request.urlopen(url, timeout=2) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(delay)
    return False

def _apply_string_overrides(workflow: dict, overrides: dict):
    """Very simple string replace inside node properties for common loaders/savers."""
    if not overrides:
        return workflow
    def replace_in_value(val):
        if isinstance(val, str):
            for k, v in overrides.items():
                if v and isinstance(v, str) and v.strip():
                    # Do not blindly replace—only swap placeholders if present
                    # Placeholders we look for:
                    #   {INPUT_PATH}, {REF_IMAGE}, {OUTPUT_PATH}
                    ph = {
                        "LEVL_INPUT_DIR": "{INPUT_PATH}",
                        "LEVL_REF_IMAGE": "{REF_IMAGE}",
                        "LEVL_OUTPUT_DIR": "{OUTPUT_PATH}",
                    }.get(k)
                    if ph and ph in val:
                        val = val.replace(ph, v)
            return val
        if isinstance(val, list):
            return [replace_in_value(x) for x in val]
        if isinstance(val, dict):
            return {kk: replace_in_value(vv) for kk, vv in val.items()}
        return val

    wf = json.loads(json.dumps(workflow))  # deep copy
    # ComfyUI workflows generally have either top-level keys or a {"workflow": {...}}
    graph = wf.get("workflow", wf)
    # try to walk nodes -> properties/inputs
    for node in graph.get("nodes", []):
        for field in ("properties", "widgets_values", "inputs"):
            if field in node and node[field] is not None:
                node[field] = replace_in_value(node[field])
    if "workflow" in wf:
        wf["workflow"] = graph
        return wf
    return graph

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workflow", required=True, help="Path to ComfyUI workflow JSON")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", default=8188, type=int)
    args = ap.parse_args()

    with open(args.workflow, "r", encoding="utf-8") as f:
        wf = json.load(f)

    overrides = {
        "LEVL_INPUT_DIR": os.environ.get("LEVL_INPUT_DIR", "").strip(),
        "LEVL_REF_IMAGE": os.environ.get("LEVL_REF_IMAGE", "").strip(),
        "LEVL_OUTPUT_DIR": os.environ.get("LEVL_OUTPUT_DIR", "").strip(),
    }

    wf = _apply_string_overrides(wf, overrides)

    print(f"[levl] Waiting for ComfyUI at http://{args.host}:{args.port} ...")
    if not _wait_for_server(args.host, args.port):
        print("[levl] ERROR: ComfyUI did not come up in time.", file=sys.stderr)
        sys.exit(2)

    client_id = f"levl-{uuid.uuid4()}"
    payload = {"prompt": wf if "prompt" in wf else wf, "client_id": client_id}
    try:
        resp = _http_post(f"http://{args.host}:{args.port}/prompt", payload)
        print(f"[levl] Submitted workflow. Response: {resp}")
        print("[levl] Open UI: http://127.0.0.1:8188")
        sys.exit(0)
    except error.HTTPError as e:
        print(f"[levl] HTTPError: {e.status} {e.reason}", file=sys.stderr)
        print(e.read().decode("utf-8"), file=sys.stderr)
    except Exception as e:
        print(f"[levl] ERROR: {e}", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    main()