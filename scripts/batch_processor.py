#!/usr/bin/env python3
"""
Batch Asset Processor
Process multiple assets for optimization, conversion, or validation
"""

import bpy
import os
import json
from pathlib import Path
import argparse

PROJECT_ROOT = Path(__file__).parent.parent

class AssetProcessor:
    def __init__(self):
        self.assets_json_path = PROJECT_ROOT / "json" / "assets.json"
        self.load_assets()
        self.report = []
    
    def load_assets(self):
        """Load assets configuration"""
        with open(self.assets_json_path, 'r') as f:
            self.assets = json.load(f)
    
    def validate_all_assets(self):
        """Validate all asset paths and report missing files"""
        print("Validating all assets...")
        
        for category in ['characters', 'props', 'environments', 'fx', 'materials', 'cameras']:
            if category not in self.assets:
                continue
                
            for asset_id, asset_data in self.assets[category].items():
                filepath = asset_data.get('filepath', '')
                if filepath.startswith('//'):
                    filepath = PROJECT_ROOT / filepath[2:]
                else:
                    filepath = Path(filepath)
                
                if asset_data.get('import_type') == 'procedural':
                    status = 'PROCEDURAL'
                elif filepath.exists():
                    status = 'FOUND'
                else:
                    status = 'MISSING'
                
                self.report.append({
                    'category': category,
                    'asset_id': asset_id,
                    'filepath': str(filepath),
                    'status': status
                })
                
                print(f"  [{status}] {category}/{asset_id}")
    
    def optimize_textures(self, max_size=2048):
        """Optimize texture sizes for all assets"""
        print(f"Optimizing textures (max size: {max_size}x{max_size})...")
        
        texture_extensions = ['.png', '.jpg', '.jpeg', '.tiff', '.exr']
        textures_found = 0
        
        # Find all texture files
        for root, dirs, files in os.walk(PROJECT_ROOT / "assets"):
            for file in files:
                if any(file.lower().endswith(ext) for ext in texture_extensions):
                    filepath = Path(root) / file
                    textures_found += 1
                    print(f"  Found texture: {filepath.name}")
                    # Here you would add actual texture optimization logic
                    # using PIL or Blender's image processing
        
        print(f"Found {textures_found} textures")
    
    def convert_formats(self, source_format='.fbx', target_format='.glb'):
        """Convert assets between formats"""
        print(f"Converting {source_format} to {target_format}...")
        
        for category in ['characters', 'props', 'environments']:
            if category not in self.assets:
                continue
                
            for asset_id, asset_data in self.assets[category].items():
                filepath = asset_data.get('filepath', '')
                if filepath.endswith(source_format):
                    source_path = PROJECT_ROOT / filepath[2:] if filepath.startswith('//') else Path(filepath)
                    target_path = source_path.with_suffix(target_format)
                    
                    if source_path.exists():
                        print(f"  Converting: {asset_id}")
                        self.convert_file(source_path, target_path)
    
    def convert_file(self, source_path, target_path):
        """Convert a single file between formats"""
        # Clear scene
        bpy.ops.wm.read_homefile(use_empty=True)
        
        # Import source file
        ext = source_path.suffix.lower()
        if ext == '.fbx':
            bpy.ops.import_scene.fbx(filepath=str(source_path))
        elif ext in ['.glb', '.gltf']:
            bpy.ops.import_scene.gltf(filepath=str(source_path))
        
        # Export to target format
        target_ext = target_path.suffix.lower()
        if target_ext == '.fbx':
            bpy.ops.export_scene.fbx(filepath=str(target_path))
        elif target_ext in ['.glb', '.gltf']:
            bpy.ops.export_scene.gltf(filepath=str(target_path))
        
        print(f"    Saved: {target_path}")
    
    def generate_lods(self, levels=3):
        """Generate LOD versions for all meshes"""
        print(f"Generating {levels} LOD levels...")
        
        for category in ['characters', 'props', 'environments']:
            if category not in self.assets:
                continue
                
            for asset_id, asset_data in self.assets[category].items():
                filepath = asset_data.get('filepath', '')
                if filepath:
                    source_path = PROJECT_ROOT / filepath[2:] if filepath.startswith('//') else Path(filepath)
                    if source_path.exists():
                        print(f"  Generating LODs for: {asset_id}")
                        # Here you would add LOD generation logic
                        # using Blender's decimate modifier
    
    def create_asset_thumbnails(self, size=256):
        """Generate thumbnail images for all assets"""
        print(f"Generating {size}x{size} thumbnails...")
        
        thumbnails_dir = PROJECT_ROOT / "thumbnails"
        thumbnails_dir.mkdir(exist_ok=True)
        
        for category in ['characters', 'props', 'environments']:
            if category not in self.assets:
                continue
                
            category_dir = thumbnails_dir / category
            category_dir.mkdir(exist_ok=True)
            
            for asset_id, asset_data in self.assets[category].items():
                print(f"  Rendering thumbnail: {asset_id}")
                # Here you would add thumbnail rendering logic
                # using Blender's render engine
    
    def save_report(self, filename="asset_report.json"):
        """Save validation report to file"""
        report_path = PROJECT_ROOT / filename
        with open(report_path, 'w') as f:
            json.dump(self.report, f, indent=2)
        print(f"Report saved to: {report_path}")

def main():
    parser = argparse.ArgumentParser(description="Batch process assets")
    parser.add_argument('--validate', action='store_true', help='Validate all asset paths')
    parser.add_argument('--optimize-textures', action='store_true', help='Optimize texture sizes')
    parser.add_argument('--convert', nargs=2, metavar=('FROM', 'TO'), help='Convert formats (e.g., .fbx .glb)')
    parser.add_argument('--generate-lods', action='store_true', help='Generate LOD versions')
    parser.add_argument('--thumbnails', action='store_true', help='Generate asset thumbnails')
    
    args = parser.parse_args()
    
    processor = AssetProcessor()
    
    if args.validate:
        processor.validate_all_assets()
        processor.save_report()
    
    if args.optimize_textures:
        processor.optimize_textures()
    
    if args.convert:
        processor.convert_formats(args.convert[0], args.convert[1])
    
    if args.generate_lods:
        processor.generate_lods()
    
    if args.thumbnails:
        processor.create_asset_thumbnails()
    
    if not any(vars(args).values()):
        print("No action specified. Use --help for options.")

if __name__ == "__main__":
    main()
