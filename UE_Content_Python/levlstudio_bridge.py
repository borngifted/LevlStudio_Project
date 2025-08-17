
import unreal
import os
from pathlib import Path

class LevlStudioUnrealBridge:
    def __init__(self):
        self.project_root = Path(r"/Volumes/Jul_23_2025/LevlStudio_Project")
        self.export_path = self.project_root / "UnrealBridge" / "outbox"
        self.import_path = self.project_root / "UnrealBridge" / "inbox"
        
        # Ensure paths exist
        self.export_path.mkdir(parents=True, exist_ok=True)
        self.import_path.mkdir(parents=True, exist_ok=True)
    
    def export_sequence_for_comfyui(self, sequence_name, level_sequence, camera_binding=None):
        """Export level sequence as image sequence for ComfyUI processing"""
        
        # Set up export path
        export_folder = self.export_path / sequence_name
        export_folder.mkdir(exist_ok=True)
        
        # Configure movie pipeline
        movie_pipeline = unreal.MoviePipelineQueueEngineSubsystem.get_queue_subsystem()
        queue = movie_pipeline.get_queue()
        
        # Create job
        job = queue.allocate_new_job(unreal.MoviePipelinePythonHostJob)
        job.set_configuration(self.create_export_config(str(export_folder)))
        
        # Set sequence
        job.sequence = unreal.SoftObjectPath(level_sequence.get_path_name())
        
        # Execute job
        movie_pipeline.render_queue_with_executor_instance(
            unreal.MoviePipelinePythonHostExecutor
        )
        
        print(f"Exported sequence to: {export_folder}")
        return str(export_folder)
    
    def create_export_config(self, output_path):
        """Create movie pipeline configuration for ComfyUI export"""
        config = unreal.MoviePipelineMasterConfig()
        
        # Output settings
        output_setting = config.find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)
        output_setting.output_directory = unreal.DirectoryPath(output_path)
        output_setting.file_name_format = "frame_{frame_number:05d}"
        
        # Image sequence settings
        image_output = config.find_or_add_setting_by_class(unreal.MoviePipelineImageSequenceOutput_PNG)
        image_output.set_editor_property("output_format", unreal.EImageFormat.PNG)
        
        # Camera settings
        camera_setting = config.find_or_add_setting_by_class(unreal.MoviePipelineCameraSetting)
        camera_setting.set_editor_property("override_camera_settings", True)
        
        # Anti-aliasing (important for ComfyUI)
        aa_setting = config.find_or_add_setting_by_class(unreal.MoviePipelineAntiAliasingSetting)
        aa_setting.set_editor_property("spatial_sample_count", 1)
        aa_setting.set_editor_property("temporal_sample_count", 1)
        
        # Console variables (disable auto-exposure, motion blur)
        console_setting = config.find_or_add_setting_by_class(unreal.MoviePipelineConsoleVariableSetting)
        console_vars = [
            {"name": "r.DefaultFeature.AutoExposure", "value": "0"},
            {"name": "r.DefaultFeature.MotionBlur", "value": "0"},
            {"name": "r.PostProcessAAQuality", "value": "6"},
            {"name": "r.TemporalAA.Upsampling", "value": "0"}
        ]
        
        for var in console_vars:
            console_setting.console_variables.add_item(
                unreal.MoviePipelineConsoleVariableEntry(var["name"], var["value"])
            )
        
        return config
    
    def import_stylized_sequence(self, sequence_name):
        """Import stylized sequence back into Unreal"""
        
        # Look for processed images
        processed_folder = self.import_path / sequence_name
        if not processed_folder.exists():
            print(f"No processed sequence found: {sequence_name}")
            return None
        
        # Import image sequence
        import_task = unreal.AssetImportTask()
        import_task.set_editor_property("automated", True)
        import_task.set_editor_property("destination_path", f"/Game/LevlStudio/Stylized/{sequence_name}")
        import_task.set_editor_property("filename", str(processed_folder))
        import_task.set_editor_property("replace_existing", True)
        import_task.set_editor_property("save", True)
        
        # Execute import
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([import_task])
        
        print(f"Imported stylized sequence: {sequence_name}")
        return import_task.get_editor_property("imported_object_paths")

# Example usage:
# bridge = LevlStudioUnrealBridge()
# bridge.export_sequence_for_comfyui("my_sequence", my_level_sequence)
        