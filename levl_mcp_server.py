
import argparse, json, os, subprocess
from typing import Any, Dict, List, Optional

try:
    from mcp.server.fastmcp import FastMCP
except Exception as e:
    print("Missing MCP server lib. Install with: pip install 'mcp[server]'")
    raise

def _have_openai():
    try:
        import openai
        return True
    except Exception:
        return False

def _have_gemini():
    try:
        import google.generativeai as genai
        return True
    except Exception:
        return False

def _blender_cmd(blender_path: str, runner_py: str, addon_py: str, assets_json: str, scenes_json: str, project_root: str, operator: str, operator_args: Dict[str, Any]) -> List[str]:
    op_args = ['--op', operator, '--assets', assets_json, '--scenes', scenes_json, '--project', project_root, '--addon', addon_py]
    for k, v in operator_args.items():
        if isinstance(v, (dict, list)):
            op_args += [f'--{k}', json.dumps(v)]
        elif v is None:
            continue
        else:
            op_args += [f'--{k}', str(v)]
    return [blender_path, '-b', '-P', runner_py, '--'] + op_args

def _run_blender(args, operator, operator_args) -> Dict[str, Any]:
    cmd = _blender_cmd(args.blender, args.runner, args.addon, args.assets, args.scenes, args.project, operator, operator_args)
    p = subprocess.run(cmd, capture_output=True, text=True)
    out = {'returncode': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}
    try:
        last = p.stdout.strip().splitlines()[-1]
        out['result'] = json.loads(last)
    except Exception:
        pass
    return out

def _read_json_file(path: str) -> Optional[Dict[str, Any]]:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None

def _llm_openai(prompt: str, model: Optional[str], temperature: float) -> str:
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return 'ERROR: OPENAI_API_KEY not set.'
    if not _have_openai():
        return "ERROR: 'openai' package not installed. pip install openai"
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        m = model or 'gpt-4o-mini'
        resp = client.chat.completions.create(
            model=m,
            temperature=temperature,
            messages=[
                {"role":"system","content":"You are a Blender pipeline/add-on engineering assistant. Return concise, actionable fixes."},
                {"role":"user","content":prompt}
            ]
        )
        return resp.choices[0].message.content or ''
    except Exception as e:
        return f'ERROR calling OpenAI: {e}'

def _llm_gemini(prompt: str, model: Optional[str], temperature: float) -> str:
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        return 'ERROR: GOOGLE_API_KEY not set.'
    if not _have_gemini():
        return "ERROR: 'google-generativeai' package not installed. pip install google-generativeai"
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        m = model or 'gemini-1.5-flash'
        g = genai.GenerativeModel(m)
        resp = g.generate_content(prompt, generation_config={'temperature': temperature})
        return resp.text or ''
    except Exception as e:
        return f'ERROR calling Gemini: {e}'

def _troubleshoot_prompt(scene_id: str, assets_json: str, scenes_json: str, resolve: Dict[str, Any], stdout: str, stderr: str, max_log_chars: int = 4000) -> str:
    assets = _read_json_file(assets_json)
    scenes = _read_json_file(scenes_json)
    logs = (stdout or '') + '\n' + (stderr or '')
    logs = logs[-max_log_chars:] if len(logs) > max_log_chars else logs
    return f"""
You are helping fix a Blender 4.4 JSON-driven scene builder add-on (LevlStudio).
We build scenes by importing/linking assets from assets.json and scenes.json.

SCENE ID:
{scene_id}

RESOLVE REPORT (raw):
{json.dumps(resolve, indent=2)}

CURRENT assets.json (abridged):
{json.dumps(assets, indent=2) if assets else 'N/A'}

CURRENT scenes.json (abridged):
{json.dumps(scenes, indent=2) if scenes else 'N/A'}

BLENDER STDOUT/STDERR (tail):
{logs}

TASKS:
1) Identify likely causes for 'procedural' or missing assets.
2) Propose concrete fixes (file paths, import_type, collection names, transforms).
3) If relevant, output corrected assets.json and/or scenes.json as JSON.

OUTPUT FORMAT (strict JSON with keys):
{{
  "suggestions": ["..."],
  "proposed_assets_json": {{}},
  "proposed_scenes_json": {{}}
}}
"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--blender', required=True)
    ap.add_argument('--addon', required=True)
    ap.add_argument('--assets', required=True)
    ap.add_argument('--scenes', required=True)
    ap.add_argument('--project', required=True)
    ap.add_argument('--runner', default=os.path.join(os.path.dirname(__file__), 'blender_operator_runner.py'))
    ap.add_argument('--host', default='127.0.0.1')
    ap.add_argument('--port', type=int, default=8765)
    args = ap.parse_args()

    server = FastMCP('levlstudio-mcp')

    @server.tool()
    def load_json_and_list_scenes() -> dict:
        return _run_blender(args, 'levl.list_scenes', {})

    @server.tool()
    def build_scene(scene_id: str, camera_override: str = '', time_override: str = '', export_glb: str = '', export_fbx: str = '', preview_png: str = '') -> dict:
        return _run_blender(args, 'levl.build_scene_and_optional_export', {
            'scene_id': scene_id,
            'camera_override': camera_override,
            'time_override': time_override,
            'export_glb': export_glb,
            'export_fbx': export_fbx,
            'preview_png': preview_png
        })

    @server.tool()
    def resolve_report(scene_id: str) -> dict:
        return _run_blender(args, 'levl.build_scene_report_only', {'scene_id': scene_id})

    @server.tool()
    def troubleshoot_scene(scene_id: str, provider: str = 'openai', model: str = '', temperature: float = 0.2) -> dict:
        rep = _run_blender(args, 'levl.build_scene_report_only', {'scene_id': scene_id})
        result = rep.get('result') or {}
        prompt = _troubleshoot_prompt(scene_id, args.assets, args.scenes, result, rep.get('stdout',''), rep.get('stderr',''))
        provider_l = (provider or 'openai').lower()
        if provider_l == 'gemini':
            text = _llm_gemini(prompt, model or 'gemini-1.5-flash', temperature)
            used_p, used_m = 'gemini', (model or 'gemini-1.5-flash')
        else:
            text = _llm_openai(prompt, model or 'gpt-4o-mini', temperature)
            used_p, used_m = 'openai', (model or 'gpt-4o-mini')
        suggestions = text
        proposed_assets = None; proposed_scenes = None
        try:
            import re
            blocks = re.findall(r'\{(?:[^{}]|(?R))*\}', text, flags=re.DOTALL)
            if blocks:
                blocks_sorted = sorted(blocks, key=len, reverse=True)
                for blk in blocks_sorted:
                    try:
                        obj = json.loads(blk)
                        if 'suggestions' in obj or 'proposed_assets_json' in obj or 'proposed_scenes_json' in obj:
                            suggestions = obj.get('suggestions', suggestions)
                            proposed_assets = obj.get('proposed_assets_json')
                            proposed_scenes = obj.get('proposed_scenes_json')
                            break
                    except Exception:
                        continue
        except Exception:
            pass
        return {
            'ok': True,
            'llm_provider': used_p,
            'llm_model': used_m,
            'resolve_report_raw': result,
            'suggestions_text': suggestions if isinstance(suggestions, str) else json.dumps(suggestions, indent=2),
            'proposed_assets_json': proposed_assets,
            'proposed_scenes_json': proposed_scenes
        }

    print(f"LevlStudio MCP server listening on {args.host}:{args.port}")
    server.run()

if __name__ == '__main__':
    main()
