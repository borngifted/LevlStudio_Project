#!/bin/bash
# Character Organization Script for LevlStudio Project

echo "🎭 Organizing Character Files for The 13th Night"
echo "================================================"

# Set paths
SOURCE_DIR="/Users/workofficial/Desktop/The_13th_Night/13th_Characters/Characters/Upscaled_Characters"
DEST_DIR="/Users/workofficial/Desktop/The_13th_Night/LevlStudio_Project/assets/characters"

# Function to copy character files
copy_character() {
    local source_name=$1
    local dest_name=$2
    local version=${3:-v001}
    
    echo "Processing $source_name -> $dest_name..."
    
    # Create character folder structure
    mkdir -p "$DEST_DIR/$dest_name/tex"
    mkdir -p "$DEST_DIR/$dest_name/rig"
    
    # Copy GLB file if exists
    if [ -f "$SOURCE_DIR/${source_name}.glb" ]; then
        cp "$SOURCE_DIR/${source_name}.glb" "$DEST_DIR/$dest_name/${dest_name}_${version}.glb"
        echo "  ✅ Copied ${source_name}.glb"
    fi
    
    # Copy FBX file if exists
    if [ -f "$SOURCE_DIR/${source_name}.fbx" ]; then
        cp "$SOURCE_DIR/${source_name}.fbx" "$DEST_DIR/$dest_name/${dest_name}_${version}.fbx"
        echo "  ✅ Copied ${source_name}.fbx"
    fi
    
    # Copy PNG texture/reference if exists
    if [ -f "$SOURCE_DIR/${source_name}.png" ]; then
        cp "$SOURCE_DIR/${source_name}.png" "$DEST_DIR/$dest_name/tex/${dest_name}_reference.png"
        echo "  ✅ Copied reference image"
    fi
}

# Main characters
echo ""
echo "📦 Copying Main Characters..."
copy_character "Nimble" "char_nimble" "v001"
copy_character "Pip" "char_pip" "v001"
copy_character "Pip_2" "char_pip" "v002"
copy_character "Jingle" "char_jingles" "v001"

# Antagonists
echo ""
echo "👹 Copying Antagonists..."
copy_character "Evil_elf_1" "char_evil_elf_1" "v001"
copy_character "Evil_elf_4" "char_evil_elf_4" "v001"
copy_character "Evil_elf_5" "char_evil_elf_5" "v001"

# Supporting characters
echo ""
echo "🎅 Copying Supporting Characters..."
copy_character "Santa" "char_santa" "v001"
copy_character "Santa_" "char_santa" "v002"
copy_character "Crinkle" "char_crinkle" "v001"
copy_character "Fenn" "char_fenn" "v001"
copy_character "Fin2" "char_fin" "v001"
copy_character "Fin3" "char_fin" "v002"
copy_character "Glitch" "char_glitch" "v001"
copy_character "Glitch_2" "char_glitch" "v002"
copy_character "Jax" "char_jax" "v001"
copy_character "Marzipan_Maw" "char_marzipan_maw" "v001"
copy_character "The_Caroler" "char_caroler" "v001"
copy_character "Thistle_2" "char_thistle" "v001"
copy_character "Sock_snatcher" "char_sock_snatcher" "v001"
copy_character "Warth_Wrangler" "char_wrath_wrangler" "v001"
copy_character "cat" "char_gnome_cat" "v001"

# Handle Marzipan_Maw textures
echo ""
echo "🎨 Copying Marzipan_Maw textures..."
if [ -d "$SOURCE_DIR/Marzipan_Maw.fbm" ]; then
    cp "$SOURCE_DIR/Marzipan_Maw.fbm/"*.jpg "$DEST_DIR/char_marzipan_maw/tex/" 2>/dev/null
    echo "  ✅ Copied texture files"
fi

# Also check parent directory for additional files
PARENT_DIR="/Users/workofficial/Desktop/The_13th_Night/13th_Characters/Characters"
echo ""
echo "📂 Checking parent directory for additional files..."

# Copy Maz files (might be Marzipan)
if [ -f "$PARENT_DIR/Maz.fbx" ]; then
    cp "$PARENT_DIR/Maz.fbx" "$DEST_DIR/char_marzipan_maw/char_marzipan_maw_v003.fbx"
    echo "  ✅ Copied Maz.fbx as Marzipan v003"
fi

if [ -d "$PARENT_DIR/Maz.fbm" ]; then
    cp "$PARENT_DIR/Maz.fbm/"*.jpg "$DEST_DIR/char_marzipan_maw/tex/" 2>/dev/null
    echo "  ✅ Copied Maz textures"
fi

# Copy the other GLB file (YVO3D might be another character)
if [ -f "$PARENT_DIR/YVO3D_18881.glb" ]; then
    mkdir -p "$DEST_DIR/char_yvo"
    cp "$PARENT_DIR/YVO3D_18881.glb" "$DEST_DIR/char_yvo/char_yvo_v001.glb"
    echo "  ✅ Copied YVO3D as new character"
fi

echo ""
echo "✨ Character organization complete!"
echo "📍 Characters organized in: $DEST_DIR"
echo ""
echo "Next steps:"
echo "1. Update assets.json with the new character definitions"
echo "2. Test loading in Blender with the LevlStudio addon"
echo "3. Add any missing textures or rigs as needed"
