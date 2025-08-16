
import bpy, sys, json, os

def _arg(name: str, default=None):
    if '--' in sys.argv:
        idx = sys.argv.index('--'); args = sys.argv[idx+1:]
    else:
        args = []
    if name in args:
        i = args.index(name); val = args[i+1] if i+1 < len(args) else ''
        try: return json.loads(val)
        except Exception: return val
    return default

def _ensure_addon(addon_py):
    if not addon_py or not os.path.exists(addon_py): return False, {}
    with open(addon_py, 'r', encoding='utf-8') as f: code = f.read()
    g = {'__name__': '__main__'}
    exec(compile(code, addon_py, 'exec'), g, g)
    if 'register' in g:
        try: g['register']()
        except Exception: pass
    return True, g

def _load_loader(LevlStudioLoader, assets, scenes):
    ldr = LevlStudioLoader(assets_path=assets, scenes_path=scenes)
    ldr.load_all(); return ldr

def main():
    op = _arg('--op',''); addon=_arg('--addon',''); assets=_arg('--assets',''); scenes=_arg('--scenes',''); scene_id=_arg('--scene_id',''); camera_override=_arg('--camera_override',''); time_override=_arg('--time_override',''); export_glb=_arg('--export_glb',''); export_fbx=_arg('--export_fbx',''); preview_png=_arg('--preview_png','')
    ok, g = _ensure_addon(addon)
    if not ok:
        print(json.dumps({'ok': False, 'error': 'Addon not found'})); return
    LEVL_Utilities = g.get('LEVL_Utilities'); LevlStudioLoader = g.get('LevlStudioLoader')
    ldr = _load_loader(LevlStudioLoader, assets, scenes)
    report = {'op': op, 'scene_id': scene_id, 'ok': True}
    try:
        if op == 'levl.list_scenes':
            report['scenes'] = ldr.list_scene_ids()
        elif op == 'levl.build_scene_report_only':
            sd = ldr.get_scene(scene_id)
            if not sd: raise RuntimeError(f'Scene not found: {scene_id}')
            coll = LEVL_Utilities.ensure_collection(sd['scene_id']); LEVL_Utilities.clear_collection(coll)
            LEVL_Utilities.build_environment(sd, ldr); LEVL_Utilities.apply_lighting(sd, time_override, ldr); LEVL_Utilities.apply_camera(sd, camera_override, ldr); LEVL_Utilities.spawn_props(sd, ldr)
            report['resolve_report'] = list(bpy.context.scene.get('LEVLS_resolve_report', []))
        elif op == 'levl.build_scene_and_optional_export':
            sd = ldr.get_scene(scene_id)
            if not sd: raise RuntimeError(f'Scene not found: {scene_id}')
            coll = LEVL_Utilities.ensure_collection(sd['scene_id']); LEVL_Utilities.clear_collection(coll)
            LEVL_Utilities.build_environment(sd, ldr); LEVL_Utilities.apply_lighting(sd, time_override, ldr); LEVL_Utilities.apply_camera(sd, camera_override, ldr); LEVL_Utilities.spawn_props(sd, ldr)
            class _P: pass
            p = _P(); p.preview_still_path=preview_png; p.export_fbx_path=export_fbx; p.export_gltf_path=export_glb
            LEVL_Utilities.export_all(p)
            report['exports'] = {'preview': preview_png, 'fbx': export_fbx, 'glb': export_glb}
        else:
            report['ok'] = False; report['error'] = f'Unknown op: {op}'
    except Exception as e:
        report['ok'] = False; report['error'] = str(e)
    print(json.dumps(report))

if __name__ == '__main__':
    main()
