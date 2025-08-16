# Style Reference Guide - The 13th Night

## Style Images for AI Transfer

Place these style reference images in the `refs/` folder. Each should be 1024x1024 or 512x512 PNG format.

### 🎄 style_festive_night.png
**Christmas Night Atmosphere**
- Deep blue night sky with stars
- Warm golden lights from windows
- Snow-covered rooftops
- Soft glowing street lamps
- Red and green accent colors
- Cozy festive mood

### ❄️ style_ice_crystal.png
**Frozen Crystalline Look**
- Sharp geometric ice formations
- Blue-white color palette
- Prismatic light refractions
- Frost patterns and fractals
- Translucent/transparent elements
- Cold, crisp atmosphere

### ✨ style_magical_glow.png
**Ethereal Magical Lighting**
- Soft purple and pink hues
- Floating particles of light
- Bioluminescent effects
- Dreamlike fog/mist
- Glowing runes or symbols
- Mystical aurora-like colors

### 🌲 style_dark_forest.png
**Dark Mysterious Forest**
- Deep shadows and silhouettes
- Muted green and brown tones
- Fog between trees
- Moonlight filtering through branches
- Gothic/horror atmosphere
- High contrast lighting

### 🍬 style_candy_cane.png
**Candy/Sweet Aesthetic**
- Bright red and white stripes
- Glossy/shiny surfaces
- Pastel pink and mint green
- Rounded, soft shapes
- Sugary textures
- Whimsical, playful mood

## Creating Your Own Styles

### Tools
- **Midjourney**: `/imagine prompt: [style description] --ar 1:1 --v 6`
- **DALL-E 3**: "Create a 1024x1024 style reference image showing..."
- **Stable Diffusion**: Use img2img with style LoRAs
- **Photoshop**: Paint or composite manually

### Tips
1. **Consistency**: Keep color palette limited (3-5 main colors)
2. **Mood**: Focus on lighting and atmosphere over details
3. **Texture**: Include distinctive surface qualities
4. **Contrast**: Balance light and dark areas
5. **Signature Elements**: Add unique visual motifs

### Example Prompts

**Midjourney**:
```
festive Christmas village at night, warm golden window lights, 
deep blue sky, snow covered roofs, cozy atmosphere, style reference 
image, painted illustration style --ar 1:1 --v 6
```

**DALL-E 3**:
```
Create a 1024x1024 style reference image showing a magical ethereal 
atmosphere with soft purple and pink glowing particles, mystical fog, 
aurora-like colors in the sky, dreamlike quality, suitable for AI 
style transfer
```

**Stable Diffusion**:
```
(ice crystal formations:1.4), prismatic light, blue white palette, 
geometric patterns, frost fractals, translucent, sharp edges, 
cold atmosphere, style reference, high quality
Negative: blurry, low quality, text, watermark
```

## Style Mixing

You can combine styles by:
1. Using multiple style images in sequence
2. Blending two styles in Photoshop
3. Adjusting style_strength in the ComfyUI workflow

### Recommended Combinations
- **Festive + Magical**: Holiday magic aesthetic
- **Ice + Dark Forest**: Frozen horror mood
- **Candy + Magical**: Whimsical fantasy
- **Festive + Ice**: Winter wonderland

## File Naming Convention

```
style_[mood]_[variant].png
```

Examples:
- `style_festive_night_v1.png`
- `style_ice_crystal_blue.png`
- `style_magical_glow_purple.png`

## Testing Styles

Quick test command:
```bash
python3 ue_to_comfy_oneclick.py \
  --level "/Game/Test/EmptyLevel" \
  --bp_path "/Game/Test/BP_Cube" \
  --movie_out "./exports/style_test.mp4" \
  --style_img "./refs/style_[YOUR_STYLE].png" \
  --resolution "512x512" \
  --fps 12
```

This renders faster for style testing (lower res, fewer frames).

---

*Remember: Style images heavily influence the final look. Spend time crafting good references!*
