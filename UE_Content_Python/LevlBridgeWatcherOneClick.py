#!/usr/bin/env python3
"""
LevlStudio One-Click UE Python Watcher
Handles oneclick_build_and_render action using Movie Render Queue
Place this in: YourUEProject/Content/Python/LevlBridgeWatcherOneClick.py
"""
import unreal, json, os, glob, traceback, time

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
    Main action: spawn Blueprint, create Level Sequence, add camera, render with MRQ
    """
    p = cmd["payload"]
    level = p.get("level_path", "/Game/Levl/Maps/Empty")
    bp_path = p["bp_path"]
    out_path = p.get("output_movie_path", f"{unreal.Paths.project_dir().rstrip('/')}/Saved/Movies/oneclick.mp4")
    res = p.get("resolution", "1280x720")
    fps = int(p.get("fps", 24))
    loc = _parse_vec(p.get("spawn_location", "0,0,300"))
    rot = _parse_rot(p.get("spawn_rotation", "0,0,0"))
    seq_name = p.get("sequence_name", "Seq_OneClick")

    print(f"🎬 Starting One-Click Render: {bp_path} in {level}")

    # Step 1: Load level
    print(f"📁 Loading level: {level}")
    if not unreal.EditorLevelLibrary.load_level(level):
        raise RuntimeError(f"Failed to load level: {level}")

    # Step 2: Spawn actor from Blueprint
    print(f"🎭 Spawning Blueprint: {bp_path}")
    bp = _load_asset(bp_path)
    if not bp:
        raise RuntimeError(f"Blueprint not found: {bp_path}")
    
    actor = unreal.EditorLevelLibrary.spawn_actor_from_object(bp, loc, rot)
    if not actor:
        raise RuntimeError(f"Failed to spawn actor from: {bp_path}")

    # Step 3: Create Level Sequence
    print(f"🎞️ Creating Level Sequence: {seq_name}")
    seq_factory = unreal.LevelSequenceFactoryNew()
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    package_path = "/Game/LevlStudio/Sequences"
    
    # Ensure directory exists
    if not unreal.EditorAssetLibrary.does_directory_exist(package_path):
        unreal.EditorAssetLibrary.make_directory(package_path)
    
    # Create unique sequence name to avoid conflicts
    seq_name_unique = f"{seq_name}_{int(time.time())}"
    seq = asset_tools.create_asset(seq_name_unique, package_path, unreal.LevelSequence, seq_factory)
    
    if not seq:
        raise RuntimeError(f"Failed to create Level Sequence: {seq_name_unique}")

    # Step 4: Add CineCameraActor
    print("📹 Adding Cine Camera")
    camera_loc = unreal.Vector(loc.x, loc.y - 500, loc.z + 200)  # Position camera relative to spawned actor
    camera_rot = unreal.Rotator(-10, 0, 0)  # Slight downward angle
    cine = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.CineCameraActor, 
        camera_loc, 
        camera_rot
    )
    
    if not cine:
        raise RuntimeError("Failed to create Cine Camera")

    # Step 5: Bind actors to sequence
    print("🔗 Binding actors to sequence")
    seq_bp_binding = seq.add_possessable(actor)
    seq_cam_binding = seq.add_possessable(cine)

    # Step 6: Add Camera Cut Track
    print("✂️ Adding camera cut track")
    cut_track = seq.add_master_track(unreal.MovieSceneCameraCutTrack)
    cut_section = cut_track.add_section()
    
    # Set sequence duration (4 seconds)
    duration_frames = fps * 4
    cut_section.set_start_frame_bounded(0)
    cut_section.set_end_frame_bounded(duration_frames)
    cut_section.set_camera_binding_id(seq_cam_binding.get_id())

    # Step 7: Configure Movie Render Queue
    print("🎬 Configuring Movie Render Queue")
    mrq_subsys = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
    queue = mrq_subsys.get_queue()
    
    # Clear existing jobs
    queue.delete_all_jobs()
    
    # Create new job
    job = queue.allocate_new_job(unreal.MoviePipelineExecutorJob)
    job.map = unreal.SoftObjectPath(level)
    job.job_name = f"OneClickJob_{int(time.time())}"
    job.sequence = unreal.SoftObjectPath(seq.get_path_name())

    # Configure job settings
    settings = job.get_configuration()
    
    # Output settings
    out_setting = settings.find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)
    out_dir = os.path.dirname(out_path)
    out_file_base = os.path.splitext(os.path.basename(out_path))[0]
    out_setting.output_directory = unreal.DirectoryPath(out_dir)
    out_setting.file_name_format = out_file_base
    
    # Resolution settings
    res_w, res_h = [int(v) for v in res.split('x')]
    res_setting = settings.find_or_add_setting_by_class(unreal.MoviePipelineResolutionSetting)
    res_setting.output_resolution = unreal.IntPoint(res_w, res_h)
    
    # Frame rate settings
    gen_setting = settings.find_or_add_setting_by_class(unreal.MoviePipelineGeneralSetting)
    gen_setting.output_frame_rate = unreal.FrameRate(fps, 1)
    
    # Output format - PNG sequence for reliability
    img_setting = settings.find_or_add_setting_by_class(unreal.MoviePipelineImageSequenceOutput_PNG)
    
    # Anti-aliasing for quality
    aa_setting = settings.find_or_add_setting_by_class(unreal.MoviePipelineAntiAliasingSetting)
    aa_setting.spatial_sample_count = 4
    aa_setting.temporal_sample_count = 4

    # Step 8: Execute render
    print("🚀 Starting render execution...")
    executor = unreal.MoviePipelinePIEExecutor()
    
    # Start rendering
    mrq_subsys.render_queue_with_executor(executor, queue)

    # Step 9: Wait for completion
    print("⏳ Waiting for render to complete...")
    max_wait_time = 300  # 5 minutes max
    start_time = time.time()
    
    while executor.is_rendering():
        if time.time() - start_time > max_wait_time:
            raise RuntimeError("Render timed out after 5 minutes")
        
        # Sleep and update progress
        unreal.SystemLibrary.delay(unreal.EditorLevelLibrary.get_editor_world(), 1.0)
        elapsed = int(time.time() - start_time)
        print(f"⏳ Rendering... {elapsed}s elapsed")

    print("✅ Render completed!")

    # Step 10: Find output files
    # For PNG sequence, we'll return the directory path
    output_dir = out_dir
    png_pattern = f"{out_file_base}.*.png"
    
    # Check if we have PNG files
    png_files = glob.glob(os.path.join(output_dir, png_pattern))
    
    result_data = {
        "movie_path": out_path if out_path.endswith('.mp4') else output_dir,
        "output_format": "mp4" if out_path.endswith('.mp4') else "png_sequence",
        "png_files": len(png_files) if png_files else 0,
        "sequence": seq.get_path_name(),
        "spawned_actor": actor.get_name(),
        "camera": cine.get_name(),
        "resolution": res,
        "fps": fps,
        "duration_frames": duration_frames
    }
    
    print(f"🎉 One-Click render complete: {result_data}")
    return result_data

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
