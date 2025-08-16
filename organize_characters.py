#!/usr/bin/env python3
"""
Character File Organizer for LevlStudio Project
Copies and renames character files from the 13th_Characters folder
"""

import os
import shutil
from pathlib import Path

# Define source and destination paths
SOURCE_DIR = Path("/Users/workofficial/Desktop/The_13th_Night/13th_Characters/Characters/Upscaled_Characters")
DEST_DIR = Path("/Users/workofficial/Desktop/The_13th_Night/LevlStudio_Project/assets/characters")

# Character mapping (source name -> destination name)
CHARACTER_MAPPING = {
    # Main characters (already in our JSON)
    "Nimble": "char_nimble",
    "Pip": "char_pip",
    "Pip_2": "char_pip",  # Alternative version
    "Jingle": "char_jingles",
    
    # Antagonists
    "Evil_elf_1": "char_evil_elf_1",
    "Evil_elf_4": "char_evil_elf_4", 
    "Evil_elf_5": "char_evil_elf_5",
    
    # Supporting characters
    "Santa": "char_santa",
    "Santa_": "char_santa",  # Alternative version
    "Crinkle": "char_crinkle",
    "Fenn": "char_fenn",
    "Fin2": "char_fin",
    "Fin3": "char_fin",  # Alternative version
    "Glitch": "char_glitch",
    "Glitch_2": "char_glitch",  # Alternative version
    "Jax": "char_jax",
    "Marzipan_Maw": "char_marzipan_maw",
    "The_Caroler": "char_caroler",
    "Thistle_2": "char_thistle",
    "Sock_snatcher": "char_sock_snatcher",
    "Warth_Wrangler": "char_wrath_wrangler",
    "Yule": "char_yule",
    "cat": "char_gnome_cat",
}

def organize_characters():
    """Copy and organize character files"""
    
    results = []
    
    for source_name, dest_name in CHARACTER_MAPPING.items():
        # Create character folder
        char_folder = DEST_DIR / dest_name
        char_folder.mkdir(parents=True, exist_ok=True)
        
        # Create subfolders
        (char_folder / "tex").mkdir(exist_ok=True)
        (char_folder / "rig").mkdir(exist_ok=True)
        
        # Copy GLB file if exists
        glb_source = SOURCE_DIR / f"{source_name}.glb"
        if glb_source.exists():
            # Determine version number
            version = "v002" if source_name.endswith("_2") or source_name.endswith("_") else "v001"
            glb_dest = char_folder / f"{dest_name}_{version}.glb"
            
            if not glb_dest.exists():  # Don't overwrite existing files
                shutil.copy2(glb_source, glb_dest)
                results.append(f"✅ Copied {source_name}.glb -> {glb_dest.name}")
            else:
                results.append(f"⚠️  Skipped {source_name}.glb (already exists)")
        
        # Copy FBX file if exists
        fbx_source = SOURCE_DIR / f"{source_name}.fbx"
        if fbx_source.exists():
            fbx_dest = char_folder / f"{dest_name}_v001.fbx"
            if not fbx_dest.exists():
                shutil.copy2(fbx_source, fbx_dest)
                results.append(f"✅ Copied {source_name}.fbx -> {fbx_dest.name}")
        
        # Copy texture/reference image if exists
        png_source = SOURCE_DIR / f"{source_name}.png"
        if png_source.exists():
            png_dest = char_folder / "tex" / f"{dest_name}_reference.png"
            if not png_dest.exists():
                shutil.copy2(png_source, png_dest)
                results.append(f"✅ Copied {source_name}.png -> reference texture")
    
    # Handle special case: Marzipan_Maw has textures in .fbm folder
    marz_tex_folder = SOURCE_DIR / "Marzipan_Maw.fbm"
    if marz_tex_folder.exists():
        marz_dest = DEST_DIR / "char_marzipan_maw" / "tex"
        for tex_file in marz_tex_folder.glob("*.jpg"):
            tex_dest = marz_dest / f"char_marzipan_maw_{tex_file.stem}.jpg"
            if not tex_dest.exists():
                shutil.copy2(tex_file, tex_dest)
                results.append(f"✅ Copied Marzipan_Maw texture: {tex_file.name}")
    
    return results

def create_character_readme():
    """Create a README documenting all characters"""
    readme_content = """# Character Assets Documentation

## Main Characters
- **char_nimble**: Nimble the elf - main protagonist
- **char_pip**: Pip - tech-savvy companion (v001 and v002 available)
- **char_jingles**: Jingle - magical elf companion

## Antagonists
- **char_evil_elf_1**: Evil elf variant 1
- **char_evil_elf_4**: Evil elf variant 4
- **char_evil_elf_5**: Evil elf variant 5

## Supporting Characters
- **char_santa**: Santa Claus (multiple versions)
- **char_crinkle**: Crinkle character
- **char_fenn**: Fenn character
- **char_fin**: Fin character (multiple versions)
- **char_glitch**: Glitch character (v001 and v002)
- **char_jax**: Jax character
- **char_marzipan_maw**: Marzipan Maw with textures
- **char_caroler**: The Caroler
- **char_thistle**: Thistle character
- **char_sock_snatcher**: Sock Snatcher
- **char_wrath_wrangler**: Wrath Wrangler
- **char_yule**: Yule character
- **char_gnome_cat**: Gnome cat

## File Formats
- GLB files: Ready for import
- FBX files: Available for some characters
- PNG files: Reference images/textures in tex/ folders

## Naming Convention
- Character folders: char_[name]
- Model files: char_[name]_v[version].[ext]
- Textures: Located in tex/ subfolder
- Rigs: Located in rig/ subfolder (to be added)
"""
    
    readme_path = DEST_DIR / "README.md"
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    return "✅ Created character documentation"

if __name__ == "__main__":
    print("🎭 Character File Organizer")
    print("=" * 50)
    
    # Check if source directory exists
    if not SOURCE_DIR.exists():
        print(f"❌ Source directory not found: {SOURCE_DIR}")
        exit(1)
    
    print(f"📂 Source: {SOURCE_DIR}")
    print(f"📂 Destination: {DEST_DIR}")
    print("")
    
    # Organize files
    print("📦 Organizing character files...")
    results = organize_characters()
    
    for result in results:
        print(result)
    
    # Create documentation
    print("")
    doc_result = create_character_readme()
    print(doc_result)
    
    print("")
    print(f"✨ Complete! Organized {len(CHARACTER_MAPPING)} characters")
    print(f"   Check: {DEST_DIR}")
