#!/usr/bin/env python3
"""
Blender Automation Scripts for AI-to-3D Pipeline
Handles mesh cleanup, retopology, and UE5 export preparation
"""

import bpy
import bmesh
import mathutils
from pathlib import Path
import json
import sys
import os

class BlenderProcessor:
    """Automate Blender operations for AI-generated 3D models"""
    
    def __init__(self):
        self.ensure_clean_scene()
        
    def ensure_clean_scene(self):
        """Clear the default scene"""
        # Delete default objects
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        
        # Delete orphan data blocks
        bpy.ops.outliner.orphans_purge(do_recursive=True)
    
    def import_ai_model(self, file_path: str) -> bool:
        """Import AI-generated 3D model (GLB, OBJ, FBX)"""
        path = Path(file_path)
        
        if not path.exists():
            print(f"Error: File not found: {file_path}")
            return False
        
        try:
            if path.suffix.lower() == '.glb':
                bpy.ops.import_scene.gltf(filepath=file_path)
            elif path.suffix.lower() == '.obj':
                bpy.ops.import_scene.obj(filepath=file_path)
            elif path.suffix.lower() == '.fbx':
                bpy.ops.import_scene.fbx(filepath=file_path)
            else:
                print(f"Unsupported format: {path.suffix}")
                return False
            
            print(f"✅ Imported: {file_path}")
            return True
            
        except Exception as e:
            print(f"Import failed: {e}")
            return False
    
    def cleanup_mesh(self, target_object=None):
        """Clean up mesh topology for AI-generated models"""
        if target_object is None:
            # Get the first mesh object
            mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
            if not mesh_objects:
                print("No mesh objects found")
                return False
            target_object = mesh_objects[0]
        
        # Select and activate the object
        bpy.context.view_layer.objects.active = target_object
        target_object.select_set(True)
        
        # Enter edit mode
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Select all vertices
        bpy.ops.mesh.select_all(action='SELECT')
        
        # Cleanup operations
        print("🧹 Cleaning up mesh...")
        
        # 1. Remove doubles/merge vertices
        bpy.ops.mesh.remove_doubles(threshold=0.001)
        
        # 2. Remove degenerate faces
        bpy.ops.mesh.delete_loose()
        
        # 3. Fill holes
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_mode(type='EDGE')
        bpy.ops.mesh.select_non_manifold()
        bpy.ops.mesh.edge_face_add()
        
        # 4. Recalculate normals
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        
        # 5. Triangulate (good for game engines)
        bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
        
        # Return to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Apply smooth shading
        bpy.ops.object.shade_smooth()
        
        print("✅ Mesh cleanup complete")
        return True
    
    def retopology_remesh(self, voxel_size=0.05, target_object=None):
        """Remesh using voxel remesher (alternative to Trio Studio)"""
        if target_object is None:
            target_object = bpy.context.active_object
        
        if not target_object or target_object.type != 'MESH':
            print("No mesh object selected")
            return False
        
        # Select the object
        bpy.context.view_layer.objects.active = target_object
        target_object.select_set(True)
        
        # Add remesh modifier
        remesh_modifier = target_object.modifiers.new(name="Remesh", type='REMESH')
        remesh_modifier.mode = 'VOXEL'
        remesh_modifier.voxel_size = voxel_size
        remesh_modifier.use_remove_disconnected = True
        
        # Apply the modifier
        bpy.ops.object.modifier_apply(modifier="Remesh")
        
        print(f"✅ Retopology complete with voxel size: {voxel_size}")
        return True
    
    def decimate_mesh(self, ratio=0.5, target_object=None):
        """Reduce polygon count for game optimization"""
        if target_object is None:
            target_object = bpy.context.active_object
        
        if not target_object or target_object.type != 'MESH':
            print("No mesh object selected")
            return False
        
        # Add decimate modifier
        decimate_modifier = target_object.modifiers.new(name="Decimate", type='DECIMATE')
        decimate_modifier.ratio = ratio
        
        # Apply the modifier
        bpy.ops.object.modifier_apply(modifier="Decimate")
        
        print(f"✅ Decimation complete, reduced to {ratio*100}% of original")
        return True
    
    def setup_materials_for_ue(self, target_object=None):
        """Set up materials compatible with Unreal Engine"""
        if target_object is None:
            target_object = bpy.context.active_object
        
        if not target_object or target_object.type != 'MESH':
            return False
        
        # Create or get material
        if target_object.data.materials:
            material = target_object.data.materials[0]
        else:
            material = bpy.data.materials.new(name=f"{target_object.name}_Material")
            target_object.data.materials.append(material)
        
        # Set up material for UE5 compatibility
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        
        # Clear existing nodes
        nodes.clear()
        
        # Add principled BSDF
        principled = nodes.new(type='ShaderNodeBsdfPrincipled')
        principled.location = (0, 0)
        
        # Add output
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (300, 0)
        
        # Link them
        links.new(principled.outputs['BSDF'], output.inputs['Surface'])
        
        # Set default values suitable for games
        principled.inputs['Metallic'].default_value = 0.0
        principled.inputs['Roughness'].default_value = 0.8
        
        print("✅ UE5-compatible material setup complete")
        return True
    
    def add_collision_mesh(self, target_object=None):
        """Create collision mesh for Unreal Engine"""
        if target_object is None:
            target_object = bpy.context.active_object
        
        if not target_object or target_object.type != 'MESH':
            return False
        
        # Duplicate object for collision
        bpy.ops.object.duplicate(linked=False)
        collision_object = bpy.context.active_object
        collision_object.name = f"UCX_{target_object.name}"
        
        # Simplify collision mesh
        bpy.context.view_layer.objects.active = collision_object
        
        # Add decimate modifier for collision
        decimate_modifier = collision_object.modifiers.new(name="CollisionDecimate", type='DECIMATE')
        decimate_modifier.ratio = 0.2  # Very simplified for collision
        bpy.ops.object.modifier_apply(modifier="CollisionDecimate")
        
        # Convex hull for better collision
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.convex_hull()
        bpy.ops.object.mode_set(mode='OBJECT')
        
        print("✅ Collision mesh created")
        return True
    
    def export_for_unreal(self, export_path: str, include_collision=True):
        """Export model as FBX for Unreal Engine"""
        
        # Ensure export directory exists
        export_path = Path(export_path)
        export_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Select all mesh objects
        bpy.ops.object.select_all(action='DESELECT')
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH':
                obj.select_set(True)
        
        # Export FBX with UE5 settings
        bpy.ops.export_scene.fbx(
            filepath=str(export_path),
            use_selection=True,
            use_active_collection=False,
            global_scale=1.0,
            apply_unit_scale=True,
            apply_scale_options='FBX_SCALE_NONE',
            bake_space_transform=False,
            object_types={'MESH'},
            use_mesh_modifiers=True,
            use_custom_props=False,
            add_leaf_bones=False,
            primary_bone_axis='Y',
            secondary_bone_axis='X',
            use_armature_deform_only=False,
            armature_nodetype='NULL',
            bake_anim=False,
            path_mode='AUTO',
            embed_textures=False,
            batch_mode='OFF',
            use_batch_own_dir=True,
            use_metadata=True
        )
        
        print(f"✅ Exported to: {export_path}")
        return True
    
    def full_ai_to_ue_process(self, input_file: str, output_file: str, 
                             voxel_size=0.05, decimate_ratio=0.7):
        """Complete pipeline: Import → Clean → Retopo → Export"""
        
        print(f"🚀 Starting full AI-to-UE pipeline for: {input_file}")
        
        # Step 1: Import
        if not self.import_ai_model(input_file):
            return False
        
        # Step 2: Cleanup
        if not self.cleanup_mesh():
            return False
        
        # Step 3: Retopology
        if not self.retopology_remesh(voxel_size=voxel_size):
            return False
        
        # Step 4: Decimate for optimization
        if not self.decimate_mesh(ratio=decimate_ratio):
            return False
        
        # Step 5: Setup materials
        if not self.setup_materials_for_ue():
            return False
        
        # Step 6: Add collision
        if not self.add_collision_mesh():
            return False
        
        # Step 7: Export
        if not self.export_for_unreal(output_file):
            return False
        
        print("🎉 AI-to-UE pipeline complete!")
        return True


# Command line interface for Blender
def main():
    """Main function for command line usage"""
    
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: blender --background --python blender_automation.py -- <command> [args]")
        print("Commands:")
        print("  process <input_file> <output_file> - Full pipeline")
        print("  cleanup <input_file> - Just cleanup mesh")
        print("  export <input_file> <output_file> - Import and export")
        return
    
    # Find where Blender arguments end and ours begin
    try:
        argv_index = sys.argv.index("--") + 1
        script_args = sys.argv[argv_index:]
    except ValueError:
        script_args = []
    
    if not script_args:
        print("No command specified")
        return
    
    processor = BlenderProcessor()
    command = script_args[0]
    
    if command == "process" and len(script_args) >= 3:
        input_file = script_args[1]
        output_file = script_args[2]
        processor.full_ai_to_ue_process(input_file, output_file)
        
    elif command == "cleanup" and len(script_args) >= 2:
        input_file = script_args[1]
        processor.import_ai_model(input_file)
        processor.cleanup_mesh()
        
    elif command == "export" and len(script_args) >= 3:
        input_file = script_args[1]
        output_file = script_args[2]
        processor.import_ai_model(input_file)
        processor.cleanup_mesh()
        processor.export_for_unreal(output_file)
        
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    # Only run main if we're in Blender
    if 'bpy' in globals():
        main()