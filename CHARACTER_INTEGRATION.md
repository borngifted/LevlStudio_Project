# Character Integration Guide - The 13th Night

## 📁 Character Files Organization

### Source Location
- **Original files**: `/Users/workofficial/Desktop/The_13th_Night/13th_Characters/Characters/`
- **Upscaled versions**: `.../Upscaled_Characters/`

### Destination Structure
```
/LevlStudio_Project/assets/characters/
├── char_nimble/          # Main protagonist
├── char_pip/             # Tech companion (v001 & v002)
├── char_jingles/         # Musical magical companion
├── char_santa/           # Santa (v001 & v002)
├── char_evil_elf_1/      # Antagonist variant 1
├── char_evil_elf_4/      # Antagonist variant 4
├── char_evil_elf_5/      # Antagonist variant 5
├── char_crinkle/         # Support elf
├── char_fenn/            # Scout elf
├── char_fin/             # Aquatic elf (v001 & v002)
├── char_glitch/          # Digital chaos elf (v001 & v002)
├── char_jax/             # Warrior elf
├── char_marzipan_maw/    # Boss monster with textures
├── char_caroler/         # Musical performer
├── char_thistle/         # Nature guardian
├── char_sock_snatcher/   # Comic relief thief
├── char_wrath_wrangler/  # Main antagonist
├── char_yule/            # Ancient spirit
└── char_gnome_cat/       # Pet companion
```

## 🚀 Quick Setup

### Step 1: Run the Organization Script
```bash
cd /Users/workofficial/Desktop/The_13th_Night/LevlStudio_Project
chmod +x organize_characters.sh
./organize_characters.sh
```

This will:
- Copy all GLB/FBX files to proper folders
- Rename them with version numbers
- Copy reference images to tex/ folders
- Handle special textures (Marzipan_Maw)

### Step 2: Load in Blender
1. Open Blender
2. Enable the LevlStudio addon (if not already)
3. In the N-panel → LevlStudio tab:
   - Load `json/assets.json`
   - Load `json/scenes.json`
   - Click "Load JSON Files"
4. Select a scene and click "Build Scene"

## 📊 Character Data

### Total Characters: 19
- **3 Heroes**: Nimble, Pip, Jingles
- **6 Antagonists**: Evil Elves (3), Wrath Wrangler, Marzipan Maw, Sock Snatcher
- **9 Support**: Santa, Crinkle, Fenn, Fin, Glitch, Jax, Caroler, Thistle, Gnome Cat
- **1 Mystical**: Yule

### File Types Available
| Character | GLB | FBX | PNG Ref | Textures |
|-----------|-----|-----|---------|----------|
| Nimble | ✅ | - | ✅ | - |
| Pip | ✅ (v1,v2) | - | ✅ | - |
| Jingles | ✅ | - | - | - |
| Santa | ✅ (v1,v2) | - | - | - |
| Evil Elves | ✅ | - | ✅ | - |
| Crinkle | ✅ | ✅ | - | - |
| Marzipan_Maw | ✅ | ✅ | - | ✅ (JPG) |
| Others | ✅ | - | Some | - |

## 🎬 Scene Compositions

### Scene 1: Santa Village Night
- Heroes meet Santa and Crinkle
- Festive atmosphere with snow effects

### Scene 2: Forbidden Library
- Nimble encounters Glitch and Caroler
- Dark mysterious setting

### Scene 3: Yule Core Chamber
- Final gathering with Yule spirit
- Magical glowing atmosphere

### Scene 4: Evil Elf Confrontation
- Battle with all evil elf variants
- Wrath Wrangler leads antagonists

### Scene 5: Marzipan Maw Boss Fight
- Epic boss battle
- Multiple heroes team up

### Scene 6: Support Characters Meeting
- All allies gather
- Dawn lighting for hope

### Scene 7: Sock Snatcher Chase
- Comic relief scene
- Fast-paced action

## 🔧 Transform Defaults

Each character has preset positions:
- **Heroes**: Center stage (0,0,0) with slight offsets
- **Antagonists**: Back row (5-10 units back), rotated 180°
- **Support**: Spread around (-5 to +5 on X axis)
- **Creatures**: Smaller scale (0.6-0.8)

## 🎨 Special Considerations

### Marzipan_Maw
- Has custom textures in tex/ folder
- Includes normal maps
- Scale 2x for boss presence

### Multiple Versions
These characters have v001 and v002:
- Pip (different poses)
- Santa (outfit variations)
- Fin (color variations)
- Glitch (effect variations)

### Missing Assets to Create
- Rig files for all characters
- Additional textures for customization
- LOD versions for optimization

## 📝 Next Steps

1. **Test Import**: Run a test scene build to verify all paths
2. **Create Rigs**: Add armatures for animation
3. **Material Setup**: Apply proper materials to characters
4. **Animation Clips**: Create idle/walk/action animations
5. **LODs**: Generate lower poly versions for background use

## 🐛 Troubleshooting

### File Not Found
- Check if organize_characters.sh was run
- Verify source files exist in 13th_Characters folder
- Update paths in assets.json if needed

### Import Issues
- GLB files should import directly
- FBX may need scale adjustment
- Check Resolve Report in addon for details

### Texture Problems
- Marzipan_Maw textures in tex/ folder
- Reference PNGs are for concept, not UV maps
- May need to create proper UV-mapped textures

## 📌 Important Notes

1. **Preserve Originals**: Script copies, doesn't move files
2. **Version Control**: Use Git to track changes
3. **Naming Convention**: char_[name]_v[version].[ext]
4. **Collection Names**: Use COL_char_[name] in Blender

---

*Last Updated: Generated for The 13th Night project*
*Total Assets: 19 characters + variants*