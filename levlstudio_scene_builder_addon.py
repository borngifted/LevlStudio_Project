#!/usr/bin/env python3
"""
LevlStudio Scene Builder Addon - Enhanced Version
A comprehensive Blender addon for managing and organizing 3D assets for The 13th Night project
Includes VS Code debugging support, transform defaults, resolve reporting, and AI integration stub
"""

bl_info = {
    "name": "LevlStudio Scene Builder Enhanced",
    "author": "LevlStudio",
    "version": (2, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > N-Panel > LevlStudio",
    "description": "Enhanced scene builder with JSON loading, transform defaults, and resolve reporting",
    "warning": "",
    "doc_url": "",
    "category": "3D View",
}

import bpy
import os
import json
import math
from pathlib import Path
from bpy.props import StringProperty, BoolProperty, EnumProperty, CollectionProperty, IntProperty
from bpy.types import Panel, Operator, PropertyGroup, UIList

# Try to import debugpy for VS Code debugging
try:
    import debugpy
    DEBUGPY_AVAILABLE = True
except ImportError:
    DEBUGPY_AVAILABLE = False
    print("debugpy not installed - VS Code debugging unavailable")

# Global variables for storing loaded data
loaded_assets = {}
loaded_scenes = []
resolve_report = []
project_root = ""

class ResolveReportItem(PropertyGroup):
    """Property group for resolve report items"""
    asset_name: StringProperty(name="Asset")
    asset_type: StringProperty(name="Type")
    status: StringProperty(name="Status")
    filepath: StringProperty(name="File Path")
    message: StringProperty(name="Message")

class LevlStudioProperties(PropertyGroup):
    """Main property group for the addon"""
    assets_json_path: StringProperty(
        name="Assets JSON",
        description="Path to assets.json file",
        default="",
        subtype='FILE_PATH'
    )
    
    scenes_json_path: StringProperty(
        name="Scenes JSON",
        description="Path to scenes.json file",
        default="",
        subtype='FILE_PATH'
    )
    
    selected_scene: EnumProperty(
        name="Scene",
        description="Select scene to build",
        items=lambda self, context: get_scene_enum_items(self, context)
    )
    
    camera_override: EnumProperty(
        name="Camera Override",
        description="Override default camera",
        items=lambda self, context: get_camera_enum_items(self, context)
    )
    
    lighting_override: EnumProperty(
        name="Lighting Override",
        description="Override default lighting preset",
        items=[
            ('DEFAULT', 'Use Scene Default', 'Use default from scene'),
            ('night_snow', 'Night Snow', 'Night with snow atmosphere'),
            ('dark_interior', 'Dark Interior', 'Dark interior lighting'),
            ('magical_glow', 'Magical Glow', 'Magical glowing atmosphere'),
            ('dawn', 'Dawn', 'Dawn lighting'),
            ('midday', 'Midday', 'Bright midday sun'),
        ]
    )
    
    show_resolve_report: BoolProperty(
        name="Show Resolve Report",
        description="Show asset resolution report",
        default=False
    )
    
    debug_mode: BoolProperty(
        name="Debug Mode",
        description="Enable debug output",
        default=False
    )
    
    vs_code_debug: BoolProperty(
        name="VS Code Debug",
        description="Enable VS Code debugging (requires debugpy)",
        default=False
    )

def get_scene_enum_items(self, context):
    """Get available scenes for enum property"""
    items = [('NONE', 'Select Scene', 'Select a scene to build')]
    for i, scene in enumerate(loaded_scenes):
        items.append((str(i), scene.get('name', f'Scene {i}'), scene.get('description', '')))
    return items

def get_camera_enum_items(self, context):
    """Get available cameras for enum property"""
    items = [('DEFAULT', 'Use Scene Default', 'Use default camera from scene')]
    if loaded_assets:
        cameras = loaded_assets.get('cameras', {})
        for cam_id, cam_data in cameras.items():
            items.append((cam_id, cam_data.get('description', cam_id), ''))
    return items

class LEVLSTUDIO_OT_attach_debugger(Operator):
    """Attach VS Code debugger to Blender"""
    bl_idname = "levlstudio.attach_debugger"
    bl_label = "Attach VS Code Debugger"
    
    def execute(self, context):
        if not DEBUGPY_AVAILABLE:
            self.report({'ERROR'}, "debugpy not installed. Install with: pip install debugpy")
            return {'CANCELLED'}
        
        try:
            debugpy.listen(("localhost", 5678))
            self.report({'INFO'}, "Debugger listening on localhost:5678")
            self.report({'INFO'}, "Now attach from VS Code with Python: Remote Attach configuration")
        except RuntimeError:
            self.report({'INFO'}, "Debugger already attached")
        
        return {'FINISHED'}

class LEVLSTUDIO_OT_load_json(Operator):
    """Load JSON configuration files"""
    bl_idname = "levlstudio.load_json"
    bl_label = "Load JSON Files"
    
    def execute(self, context):
        global loaded_assets, loaded_scenes, project_root
        props = context.scene.levlstudio_props
        
        # Load assets.json
        if props.assets_json_path and os.path.exists(props.assets_json_path):
            with open(props.assets_json_path, 'r') as f:
                data = json.load(f)
                loaded_assets = data.get('assets', {})
                # Extract project root from path
                project_root = str(Path(props.assets_json_path).parent.parent)
                self.report({'INFO'}, f"Loaded {sum(len(v) for v in loaded_assets.values())} assets")
        else:
            self.report({'ERROR'}, "Assets JSON file not found")
            return {'CANCELLED'}
        
        # Load scenes.json
        if props.scenes_json_path and os.path.exists(props.scenes_json_path):
            with open(props.scenes_json_path, 'r') as f:
                data = json.load(f)
                loaded_scenes = data.get('scenes', [])
                self.report({'INFO'}, f"Loaded {len(loaded_scenes)} scenes")
        else:
            self.report({'ERROR'}, "Scenes JSON file not found")
            return {'CANCELLED'}
        
        return {'FINISHED'}

class LEVLSTUDIO_OT_build_scene(Operator):
    """Build selected scene from JSON configuration"""
    bl_idname = "levlstudio.build_scene"
    bl_label = "Build Scene"
    
    def execute(self, context):
        global resolve_report
        props = context.scene.levlstudio_props
        
        if props.selected_scene == 'NONE':
            self.report({'ERROR'}, "Please select a scene")
            return {'CANCELLED'}
        
        scene_idx = int(props.selected_scene)
        if scene_idx >= len(loaded_scenes):
            self.report({'ERROR'}, "Invalid scene selection")
            return {'CANCELLED'}
        
        scene_data = loaded_scenes[scene_idx]
        resolve_report = []  # Clear previous report
        
        # Create main collection for scene
        scene_name = scene_data.get('name', f'Scene_{scene_idx}')
        scene_collection = bpy.data.collections.new(name=scene_name)
        context.scene.collection.children.link(scene_collection)
        
        # Process environment
        if 'environment' in scene_data:
            self.import_environment(context, scene_data['environment'], scene_collection)
        
        # Process characters
        for char_id in scene_data.get('characters', []):
            self.import_asset(context, 'characters', char_id, scene_collection)
        
        # Process props
        for prop_id in scene_data.get('props', []):
            self.import_asset(context, 'props', prop_id, scene_collection)
        
        # Process effects
        for fx_id in scene_data.get('effects', []):
            self.import_asset(context, 'fx', fx_id, scene_collection)
        
        # Process cameras
        camera_to_use = props.camera_override if props.camera_override != 'DEFAULT' else scene_data.get('default_camera')
        for cam_id in scene_data.get('cameras', []):
            obj = self.import_asset(context, 'cameras', cam_id, scene_collection)
            if cam_id == camera_to_use and obj:
                context.scene.camera = obj
        
        # Apply lighting preset
        lighting_preset = props.lighting_override if props.lighting_override != 'DEFAULT' else scene_data.get('lighting_preset')
        if lighting_preset:
            self.apply_lighting_preset(context, lighting_preset, scene_collection)
        
        # Add ground plane
        self.add_ground_plane(scene_collection)
        
        # Add volumetric fog
        self.add_volumetric_fog(scene_collection)
        
        # Update resolve report in UI
        self.update_resolve_report_ui(context)
        
        self.report({'INFO'}, f"Built scene: {scene_name}")
        return {'FINISHED'}
    
    def import_asset(self, context, category, asset_id, collection):
        """Import or link a single asset"""
        global resolve_report
        
        if category not in loaded_assets:
            self.add_resolve_entry(asset_id, category, "ERROR", "", "Category not found")
            return None
        
        asset_data = loaded_assets[category].get(asset_id)
        if not asset_data:
            self.add_resolve_entry(asset_id, category, "ERROR", "", "Asset not found in JSON")
            return None
        
        filepath = asset_data.get('filepath', '').replace('//', project_root + '/')
        import_type = asset_data.get('import_type', 'import')
        
        if not filepath or not os.path.exists(filepath):
            # Create procedural placeholder
            obj = self.create_procedural_placeholder(asset_id, asset_data, collection)
            self.add_resolve_entry(asset_id, category, "PROCEDURAL", filepath, "Created placeholder")
            return obj
        
        try:
            obj = None
            if filepath.endswith('.blend'):
                obj = self.import_blend_file(filepath, asset_data, import_type, collection)
            elif filepath.endswith(('.fbx', '.glb', '.gltf')):
                obj = self.import_3d_file(filepath, collection)
            
            if obj:
                # Apply transform defaults
                self.apply_transforms(obj, asset_data)
                self.add_resolve_entry(asset_id, category, "SUCCESS", filepath, f"Imported via {import_type}")
            
            return obj
            
        except Exception as e:
            self.add_resolve_entry(asset_id, category, "ERROR", filepath, str(e))
            return None
    
    def import_environment(self, context, env_id, collection):
        """Import environment with special handling"""
        return self.import_asset(context, 'environments', env_id, collection)
    
    def import_blend_file(self, filepath, asset_data, import_type, collection):
        """Import from .blend file using specified method"""
        collection_name = asset_data.get('collection')
        
        if import_type == 'link' and collection_name:
            # Link collection
            with bpy.data.libraries.load(filepath, link=True) as (data_from, data_to):
                if collection_name in data_from.collections:
                    data_to.collections = [collection_name]
            
            if data_to.collections:
                for col in data_to.collections:
                    collection.children.link(col)
                return col.objects[0] if col.objects else None
        
        elif import_type == 'append':
            # Append objects
            with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
                data_to.objects = data_from.objects
            
            for obj in data_to.objects:
                collection.objects.link(obj)
            
            return data_to.objects[0] if data_to.objects else None
        
        return None
    
    def import_3d_file(self, filepath, collection):
        """Import FBX/GLB/GLTF files"""
        old_objects = set(bpy.data.objects)
        
        if filepath.endswith('.fbx'):
            bpy.ops.import_scene.fbx(filepath=filepath)
        elif filepath.endswith(('.glb', '.gltf')):
            bpy.ops.import_scene.gltf(filepath=filepath)
        
        new_objects = set(bpy.data.objects) - old_objects
        
        for obj in new_objects:
            # Move to target collection
            for col in obj.users_collection:
                col.objects.unlink(obj)
            collection.objects.link(obj)
        
        return list(new_objects)[0] if new_objects else None
    
    def create_procedural_placeholder(self, name, asset_data, collection):
        """Create a procedural placeholder for missing assets"""
        asset_type = asset_data.get('type', 'prop')
        
        # Create appropriate placeholder based on type
        if asset_type == 'character':
            bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=1.8)
        elif asset_type == 'camera':
            bpy.ops.object.camera_add()
        elif asset_type == 'environment':
            bpy.ops.mesh.primitive_plane_add(size=20)
        else:
            bpy.ops.mesh.primitive_cube_add(size=1)
        
        obj = bpy.context.active_object
        obj.name = f"{name}_placeholder"
        
        # Move to collection
        for col in obj.users_collection:
            col.objects.unlink(obj)
        collection.objects.link(obj)
        
        return obj
    
    def apply_transforms(self, obj, asset_data):
        """Apply transform defaults to object"""
        if 'location' in asset_data:
            obj.location = asset_data['location']
        if 'rotation' in asset_data:
            obj.rotation_euler = asset_data['rotation']
        if 'scale' in asset_data:
            obj.scale = asset_data['scale']
    
    def apply_lighting_preset(self, context, preset_name, collection):
        """Apply lighting preset to scene"""
        # This would load lighting presets from assets.json
        # For now, create basic sun light
        light_data = bpy.data.lights.new(name=f"{preset_name}_sun", type='SUN')
        light_data.energy = 1.0
        light_obj = bpy.data.objects.new(name=f"{preset_name}_sun", object_data=light_data)
        light_obj.rotation_euler = (math.radians(45), 0, math.radians(45))
        collection.objects.link(light_obj)
    
    def add_ground_plane(self, collection):
        """Add ground plane to scene"""
        bpy.ops.mesh.primitive_plane_add(size=100, location=(0, 0, 0))
        ground = bpy.context.active_object
        ground.name = "Ground_Plane"
        
        # Move to collection
        for col in ground.users_collection:
            col.objects.unlink(ground)
        collection.objects.link(ground)
        
        # Add snow material if available
        self.apply_material_preset(ground, "mat_snow_preset")
    
    def add_volumetric_fog(self, collection):
        """Add volumetric fog to scene"""
        # Create cube for volume
        bpy.ops.mesh.primitive_cube_add(size=50, location=(0, 0, 25))
        fog_obj = bpy.context.active_object
        fog_obj.name = "Volumetric_Fog"
        
        # Move to collection
        for col in fog_obj.users_collection:
            col.objects.unlink(fog_obj)
        collection.objects.link(fog_obj)
        
        # Add volume shader
        mat = bpy.data.materials.new(name="Fog_Volume")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes.clear()
        
        # Add Principled Volume node
        volume_node = nodes.new(type='ShaderNodeVolumePrincipled')
        volume_node.inputs['Density'].default_value = 0.02
        
        output_node = nodes.new(type='ShaderNodeOutputMaterial')
        mat.node_tree.links.new(volume_node.outputs['Volume'], output_node.inputs['Volume'])
        
        fog_obj.data.materials.append(mat)
    
    def apply_material_preset(self, obj, material_name):
        """Apply material preset to object"""
        # Check if material exists or create basic one
        mat = bpy.data.materials.get(material_name)
        if not mat:
            mat = bpy.data.materials.new(name=material_name)
            mat.use_nodes = True
            
            # Create basic material based on name
            if "snow" in material_name.lower():
                mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.9, 0.9, 1.0, 1.0)
                mat.node_tree.nodes["Principled BSDF"].inputs[2].default_value = 0.5  # Subsurface
            elif "brass" in material_name.lower():
                mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.8, 0.6, 0.2, 1.0)
                mat.node_tree.nodes["Principled BSDF"].inputs[6].default_value = 1.0  # Metallic
            elif "ice" in material_name.lower():
                mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.8, 0.9, 1.0, 1.0)
                mat.node_tree.nodes["Principled BSDF"].inputs[17].default_value = 1.45  # IOR
                mat.node_tree.nodes["Principled BSDF"].inputs[21].default_value = 0.1  # Alpha
            elif "wood" in material_name.lower():
                mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.4, 0.2, 0.1, 1.0)
                mat.node_tree.nodes["Principled BSDF"].inputs[9].default_value = 0.8  # Roughness
        
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
    
    def add_resolve_entry(self, asset_name, asset_type, status, filepath, message):
        """Add entry to resolve report"""
        global resolve_report
        resolve_report.append({
            'asset_name': asset_name,
            'asset_type': asset_type,
            'status': status,
            'filepath': filepath,
            'message': message
        })
    
    def update_resolve_report_ui(self, context):
        """Update resolve report UI list"""
        scene = context.scene
        scene.levlstudio_resolve_report.clear()
        
        for entry in resolve_report:
            item = scene.levlstudio_resolve_report.add()
            item.asset_name = entry['asset_name']
            item.asset_type = entry['asset_type']
            item.status = entry['status']
            item.filepath = entry['filepath']
            item.message = entry['message']

class LEVLSTUDIO_OT_export_scene(Operator):
    """Export current scene to FBX/GLB"""
    bl_idname = "levlstudio.export_scene"
    bl_label = "Export Scene"
    
    filepath: StringProperty(
        name="File Path",
        description="Path to export file",
        default="",
        subtype='FILE_PATH'
    )
    
    export_format: EnumProperty(
        name="Format",
        description="Export format",
        items=[
            ('FBX', 'FBX', 'Export as FBX'),
            ('GLB', 'GLB', 'Export as GLB'),
            ('GLTF', 'GLTF', 'Export as GLTF'),
        ],
        default='GLB'
    )
    
    def execute(self, context):
        if not self.filepath:
            self.report({'ERROR'}, "No export path specified")
            return {'CANCELLED'}
        
        if self.export_format == 'FBX':
            bpy.ops.export_scene.fbx(filepath=self.filepath)
        elif self.export_format in ['GLB', 'GLTF']:
            bpy.ops.export_scene.gltf(filepath=self.filepath)
        
        self.report({'INFO'}, f"Exported to {self.filepath}")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class LEVLSTUDIO_OT_ai_assist(Operator):
    """AI Assistant for environment suggestions (stub)"""
    bl_idname = "levlstudio.ai_assist"
    bl_label = "AI Environment Suggest"
    
    def execute(self, context):
        # This is a stub for AI integration
        # In production, this would call OpenAI/Gemini API
        
        props = context.scene.levlstudio_props
        if props.selected_scene == 'NONE':
            self.report({'ERROR'}, "Please select a scene first")
            return {'CANCELLED'}
        
        scene_idx = int(props.selected_scene)
        scene_data = loaded_scenes[scene_idx]
        
        # Collect environment tags
        env_id = scene_data.get('environment')
        env_tags = []
        if env_id and 'environments' in loaded_assets:
            env_data = loaded_assets['environments'].get(env_id)
            if env_data:
                env_tags = env_data.get('tags', [])
        
        # This is where you'd send to AI API
        message = f"AI Stub: Would send environment tags to LLM: {env_tags}\n"
        message += "Prompt: Suggest lighting and atmosphere improvements for this environment\n"
        message += "Replace this stub with actual API call to OpenAI/Gemini"
        
        self.report({'INFO'}, message)
        print(f"AI Assistant Stub Called with tags: {env_tags}")
        
        return {'FINISHED'}

class LEVLSTUDIO_UL_resolve_report(UIList):
    """UI List for resolve report"""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # Choose icon based on status
            if item.status == "SUCCESS":
                icon = 'CHECKMARK'
            elif item.status == "ERROR":
                icon = 'ERROR'
            elif item.status == "PROCEDURAL":
                icon = 'GHOST_ENABLED'
            else:
                icon = 'QUESTION'
            
            row = layout.row()
            row.label(text=item.asset_name, icon=icon)
            row.label(text=item.asset_type)
            row.label(text=item.status)
            
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=item.asset_name)

class LEVLSTUDIO_PT_main_panel(Panel):
    """Main LevlStudio panel in N-panel"""
    bl_label = "LevlStudio Scene Builder"
    bl_idname = "LEVLSTUDIO_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "LevlStudio"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.levlstudio_props
        
        # VS Code Debug Section
        if DEBUGPY_AVAILABLE:
            box = layout.box()
            box.label(text="VS Code Debug", icon='SCRIPT')
            box.operator("levlstudio.attach_debugger", icon='PLAY')
        
        # JSON Files Section
        box = layout.box()
        box.label(text="Configuration Files", icon='FILE_FOLDER')
        box.prop(props, "assets_json_path")
        box.prop(props, "scenes_json_path")
        box.operator("levlstudio.load_json", icon='FILE_REFRESH')
        
        # Scene Building Section
        box = layout.box()
        box.label(text="Scene Building", icon='SCENE_DATA')
        box.prop(props, "selected_scene")
        
        # Overrides
        col = box.column()
        col.label(text="Overrides:")
        col.prop(props, "camera_override")
        col.prop(props, "lighting_override")
        
        # Build button
        row = box.row(align=True)
        row.scale_y = 1.5
        row.operator("levlstudio.build_scene", icon='PLAY')
        row.operator("levlstudio.export_scene", icon='EXPORT')
        
        # AI Assistant
        box = layout.box()
        box.label(text="AI Assistant", icon='LIGHT')
        box.operator("levlstudio.ai_assist", icon='AUTO')
        
        # Debug options
        box = layout.box()
        box.prop(props, "debug_mode", icon='CONSOLE')
        box.prop(props, "show_resolve_report", icon='TEXT')

class LEVLSTUDIO_PT_resolve_report(Panel):
    """Resolve report panel"""
    bl_label = "Resolve Report"
    bl_idname = "LEVLSTUDIO_PT_resolve_report"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "LevlStudio"
    bl_parent_id = "LEVLSTUDIO_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return context.scene.levlstudio_props.show_resolve_report
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        layout.template_list(
            "LEVLSTUDIO_UL_resolve_report",
            "resolve_report_list",
            scene,
            "levlstudio_resolve_report",
            scene,
            "levlstudio_resolve_report_index"
        )
        
        # Show details of selected item
        if scene.levlstudio_resolve_report_index >= 0 and scene.levlstudio_resolve_report_index < len(scene.levlstudio_resolve_report):
            item = scene.levlstudio_resolve_report[scene.levlstudio_resolve_report_index]
            box = layout.box()
            box.label(text="Details:", icon='INFO')
            col = box.column(align=True)
            col.label(text=f"Asset: {item.asset_name}")
            col.label(text=f"Type: {item.asset_type}")
            col.label(text=f"Status: {item.status}")
            if item.filepath:
                col.label(text=f"Path: {item.filepath}")
            col.label(text=f"Message: {item.message}")

# Registration
classes = [
    ResolveReportItem,
    LevlStudioProperties,
    LEVLSTUDIO_OT_attach_debugger,
    LEVLSTUDIO_OT_load_json,
    LEVLSTUDIO_OT_build_scene,
    LEVLSTUDIO_OT_export_scene,
    LEVLSTUDIO_OT_ai_assist,
    LEVLSTUDIO_UL_resolve_report,
    LEVLSTUDIO_PT_main_panel,
    LEVLSTUDIO_PT_resolve_report,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.levlstudio_props = bpy.props.PointerProperty(type=LevlStudioProperties)
    bpy.types.Scene.levlstudio_resolve_report = CollectionProperty(type=ResolveReportItem)
    bpy.types.Scene.levlstudio_resolve_report_index = IntProperty(name="Resolve Report Index", default=0)
    
    print("LevlStudio Scene Builder Enhanced - Registered")

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.levlstudio_props
    del bpy.types.Scene.levlstudio_resolve_report
    del bpy.types.Scene.levlstudio_resolve_report_index
    
    print("LevlStudio Scene Builder Enhanced - Unregistered")

if __name__ == "__main__":
    register()
