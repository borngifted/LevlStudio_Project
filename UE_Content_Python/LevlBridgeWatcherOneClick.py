# LevlStudio Bridge Watcher for Unreal Engine
# Place this in: YourUEProject/Content/Python/LevlBridgeWatcherOneClick.py
# Adds an action to spawn a BP, create a LevelSequence, and render via MRQ

import unreal, json, os, glob, traceback

BRIDGE_ROOT = unreal.Paths.project_dir() + "LevlStudioBridge/"
INBOX = BRIDGE_ROOT + "inbox/"
OUTBOX = BRIDGE_ROOT + "outbox/"

def ensure_dirs():
    for p in [BRIDGE_ROOT, INBOX, OUTBOX]:
        if not os.path.exists(p): 
            os.makedirs(p, exist_ok=True)

def _result_path(cmd_id): 
    return os.path.join(OUTBOX, f"{cmd_id}.json")

def _ok(cmd_id, data):
    with open(_result_path(cmd_id), "w", encoding="utf-8") as f:
        json.dump({"ok": True, "id": cmd_id, "data": data}, f, indent=2)

def _err(cmd_id, msg):
    with open(_result_path(cmd_id), "w", encoding="utf-8") as f:
        json.dump({"ok": False, "id": cmd_id, "error": msg}, f, indent=2)

def _parse_vec(s: str):
    try: 
        x,y,z = [float(v.strip()) for v in s.split(",")]
        return unreal.Vector(x,y,z)
    except: 
        return unreal.Vector(0,0,0)

def _parse_rot(s: str):
    try: 
        r,p,y = [float(v.strip()) for v in s.split(",")]
        return unreal.Rotator(r,p,y)
    except: 
        return unreal.Rotator(0,0,0)

def _load_asset(path): 
    return unreal.EditorAssetLibrary.load_asset(path)

def oneclick_build_and_render(cmd):
    """
    Spawn a Blueprint actor, create a LevelSequence with camera, render via Movie Render Queue
    """
    p = cmd["payload"]
    level = p.get("level_path","/Game/Levl/Maps/Empty")
    bp_path = p["bp_path"]
    out_path = p.get("output_movie_path","{proj}/Saved/Movies/oneclick.mp4".format(proj=unreal.Paths.project_dir().rstrip('/')))
    res = p.get("resolution","1280x720")
    fps = int(p.get("fps",24))
    loc = _parse_vec(p.get("spawn_location","0,0,300"))
    rot = _parse_rot(p.get("spawn_rotation","0,0,0"))
    seq_name = p.get("sequence_name","Seq_OneClick")

    # Load level
    unreal.EditorLevelLibrary.load_level(level)

    # Spawn actor from BP
    bp = _load_asset(bp_path)
    if not bp:
        raise RuntimeError(f"Blueprint not found: {bp_path}")
    actor = unreal.EditorLevelLibrary.spawn_actor_from_object(bp, loc, rot)

    # Create a LevelSequence
    seq_factory = unreal.LevelSequenceFactoryNew()
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    package_path = "/Game/Levl/Sequences"
    if not unreal.EditorAssetLibrary.does_directory_exist(package_path):
        unreal.EditorAssetLibrary.make_directory(package_path)
    seq = asset_tools.create_asset(seq_name, package_path, unreal.LevelSequence, seq_factory)

    # Add a CineCameraActor and set transform
    cine = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.CineCameraActor, 
        unreal.Vector(0,-500,300), 
        unreal.Rotator(-10,0,0)
    )
    
    # Bind actors to sequence
    seq_bp_binding = seq.add_possessable(actor)
    seq_cam_binding = seq.add_possessable(cine)

    # Add a Camera Cut Track
    cut_track = seq.add_master_track(unreal.MovieSceneCameraCutTrack)
    cut_section = cut_track.add_section()
    cut_section.set_start_frame_bounded(0)
    cut_section.set_end_frame_bounded(fps*4)  # ~4 seconds
    cut_section.set_camera_binding_id(seq_cam_binding.get_id())

    # Configure MRQ
    mrq_subsys = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
    queue = mrq_subsys.get_queue()
    job = queue.allocate_new_job(unreal.MoviePipelineExecutorJob)
    job.map = unreal.SoftObjectPath(level)
    job.job_name = "OneClickJob"
    job.sequence = unreal.SoftObjectPath(seq.get_path_name())

    # Set output and settings
    settings = job.get_configuration()
    
    # Output setting
    out_setting = settings.find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)
    out_dir = os.path.dirname(out_path)
    out_file_base = os.path.splitext(os.path.basename(out_path))[0]
    out_setting.output_directory = unreal.DirectoryPath(out_dir)
    out_setting.file_name_format = out_file_base
    
    # Resolution setting
    res_w, res_h = [int(v) for v in res.split('x')]
    res_setting = settings.find_or_add_setting_by_class(unreal.MoviePipelineResolutionSetting)
    res_setting.output_resolution = unreal.IntPoint(res_w, res_h)
    
    # FPS setting
    gen_setting = settings.find_or_add_setting_by_class(unreal.MoviePipelineGeneralSetting)
    gen_setting.output_frame_rate = unreal.FrameRate(fps,1)
    
    # Video codec (PNG sequence as fallback)
    img_setting = settings.find_or_add_setting_by_class(unreal.MoviePipelineImageSequenceOutput_PNG)

    # Execute (local)
    executor = unreal.MoviePipelinePIEExecutor()
    mrq_subsys.render_queue_with_executor(executor, queue)

    # Block until finished
    while executor.is_rendering():
        unreal.SystemLibrary.sleep(unreal.EditorLevelLibrary.get_editor_world(), 0.25)

    # Write result
    movie_guess = out_path if out_path.lower().endswith(".mp4") else os.path.join(out_dir, out_file_base + ".png")
    return {
        "movie_path": movie_guess, 
        "sequence": seq.get_path_name(), 
        "spawned": actor.get_name(), 
        "camera": cine.get_name()
    }

# Action mappings
ACTIONS = {
    "oneclick_build_and_render": oneclick_build_and_render,
}

def run_bridge_once():
    """Process all queued commands in the inbox"""
    ensure_dirs()
    processed = 0
    for path in glob.glob(INBOX + "*.json"):
        with open(path, "r", encoding="utf-8") as f:
            cmd = json.load(f)
        try:
            action = cmd["action"]
            fn = ACTIONS.get(action)
            if not fn:
                raise RuntimeError(f"Unknown action: {action}")
            data = fn(cmd)
            _ok(cmd["id"], data)
            processed += 1
        except Exception as e:
            traceback.print_exc()
            _err(cmd["id"], f"{e}")
        finally:
            try: 
                os.remove(path)
            except: 
                pass
    
    if processed > 0:
        unreal.log(f"LevlStudio Bridge: Processed {processed} commands")
    return processed

# Auto-polling timer (optional)
def start_auto_poll(interval_seconds=2.0):
    """Start auto-polling the inbox every N seconds"""
    def poll_tick(delta_time):
        run_bridge_once()
    
    # Create a timer
    unreal.EditorAssetLibrary.get_editor_world().set_timer_by_function_name(
        poll_tick, interval_seconds, True
    )
    unreal.log(f"LevlStudio Bridge: Auto-polling started (every {interval_seconds}s)")

# Menu entry to trigger once
try:
    menus = unreal.ToolMenus.get()
    menu = menus.extend_menu("LevelEditor.MainMenu")
    
    # Add Levl menu section if it doesn't exist
    if not menu.find_section("Levl"):
        menu.add_section("Levl", "LevlStudio")
    
    # Run Once entry
    entry = unreal.ToolMenuEntry(
        name="Levl.RunBridgeOnce",
        type=unreal.MultiBlockType.MENU_ENTRY,
        insert_position=unreal.ToolMenuInsert("", unreal.ToolMenuInsertType.FIRST),
    )
    entry.set_label("Levl Bridge: Run Once")
    entry.set_string_command(
        type=unreal.ToolMenuStringCommandType.PYTHON,
        custom_type="",
        string="import LevlBridgeWatcherOneClick as LB; LB.run_bridge_once()"
    )
    if not menu.find_entry("Levl.RunBridgeOnce"):
        menu.add_menu_entry("Levl", entry)
    
    # Auto-poll entry
    auto_entry = unreal.ToolMenuEntry(
        name="Levl.StartAutoPoll",
        type=unreal.MultiBlockType.MENU_ENTRY,
        insert_position=unreal.ToolMenuInsert("", unreal.ToolMenuInsertType.FIRST),
    )
    auto_entry.set_label("Levl Bridge: Start Auto-Poll")
    auto_entry.set_string_command(
        type=unreal.ToolMenuStringCommandType.PYTHON,
        custom_type="",
        string="import LevlBridgeWatcherOneClick as LB; LB.start_auto_poll(2.0)"
    )
    if not menu.find_entry("Levl.StartAutoPoll"):
        menu.add_menu_entry("Levl", auto_entry)
    
    menus.refresh_all_widgets()
    unreal.log("LevlStudio Bridge: Menu entries added")
except Exception as e:
    unreal.log_warning(f"LevlStudio Bridge: Failed to add menu entries: {e}")

# Initial setup message
unreal.log("LevlStudio Bridge Watcher loaded. Use menu: Levl Bridge → Run Once or Start Auto-Poll")
