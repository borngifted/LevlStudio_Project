# The World of STEAM - LevlStudio Demo Package

Pre-production package for adapting **The World of STEAM** into the LevlStudio pipeline. This package follows the existing demo-project pattern while keeping the core LevlStudio pipeline and the Glimmer demo unchanged.

## Project Overview

The World of STEAM begins after the global rollout of 11G, a network that promises limitless connection but drains Earth's core energy. Years later, a group of gifted young people are pulled into the living World of S.T.E.A.M., where creativity, logic, invention, and collaboration determine whether Earth can recover.

The current source set covers:

- Episode 1/prologue: 11G commercial, Dr. Tessa Falk's summit, Earth's decline, the STEAM Challenge announcement, teen introductions, selection, arrival, and first challenge setup.
- Episode 2: "The Summoning", including the active disappearance of the teens, 11G propaganda, a hacked AI Endpoint transmission, and first arrival in the World of STEAM.
- Episode 3: "The First Trial", including the mechanical landscape, Deduca's challenge, STEAM Palace propaganda, Fractal Collapse, broken music, unstable machines, and the next palace threat.

## Canon Sources

Local source PDFs remain outside this repository. This GitHub package contains derived production documentation only.

- `TWOS_Updated_Script2.pdf` is the canonical Episode 1/prologue source because it is the longest local variant.
- `TWOS_Updated_Script.pdf` and `TWOS_Updated_Script3.pdf` are duplicate/backup references for Episode 1.
- `THE WORLD OF S.T.E.A.M. - EPISODE 2: "THE SUMMONING".pdf` is canonical for Episode 2.
- `THE WORLD OF S.T.E.A.M. - EPISODE 3: "THE FIRST TRIAL".pdf` is canonical for Episode 3.

Continuity note: Episode 1 currently says eight gifted individuals are chosen, but the local source material names seven teens: Aiesha, Diana, Qawnzy, Carlos, Pyra, Alex, and Aiko. This package preserves the named seven and leaves the eighth slot unresolved.

## Demo Contents

- `docs/character_bible.md` - character roles, visual anchors, and asset IDs.
- `docs/episode_production_map.md` - episode-to-scene breakdown for Episodes 1-3.
- `docs/visual_style_guide.md` - visual language, palette, lighting, camera, and pipeline notes.
- `storyboard/world_of_steam_prompts.md` - production prompts for concept art, storyboard frames, and reference renders.
- `json/assets_world_of_steam.json` - LevlStudio-compatible asset manifest for planned characters, environments, props, FX, materials, and cameras.
- `json/scenes_world_of_steam.json` - LevlStudio-compatible scene manifest for the first production pass.
- `assets/README.md` - planned asset folder contract; no generated GLB/FBX files are included in this first pass.

## Character Lineup

- **Aiesha** - science lead from a drought-stricken Kenyan village; water systems, field repair, and applied resilience.
- **Diana** - technology lead from a struggling U.S. apartment; hacking, device repair, and systems thinking.
- **Qawnzy** - engineering lead from a garage/suburban street setting; rebellious invention, machinery, and adaptive design.
- **Carlos** - arts lead from a Colombian town square; guitar, code, rhythm, and digital symphonies.
- **Pyra** - mathematics lead from an Indian festival market; mandala geometry, sustainable pattern logic, and equation solving.
- **Alex** - nonbinary innovation/unity lead from a German lab; robotics, repair, and team integration.
- **Aiko** - precision lead from a Tokyo science fair; autonomous drones, disaster relief, and exact execution.
- **Dr. Tessa Falk** - lead scientist tied to the launch of 11G and the inciting disaster.
- **AI Endpoint** - unstable guide and hacked-transmission narrator between Earth and the World of STEAM.
- **Deduca** - calculating World of STEAM authority figure who tests the teens in Episode 3.

## Visual Direction

The demo should feel like a high-energy science-fantasy production with steampunk machinery, holographic interfaces, living mathematical architecture, broadcast satire, and corrupted educational systems. The World of STEAM is not just a backdrop; it should react to thought, creativity, music, and problem solving.

Core visual motifs:

- Gold 11G light webs over darkened cities.
- Blue-white holograms, fractal platforms, glowing code, and geometric architecture.
- Brass, copper, graphite, glass, and worn industrial surfaces.
- Glitching corporate broadcast polish contrasted with unstable rebel transmissions.
- Mechanical terrain that rises, folds, and rewrites itself during trials.

## LevlStudio Pipeline Integration

This package is a pre-production mapping layer for the existing LevlStudio workflow:

1. Use `json/assets_world_of_steam.json` to track planned production assets and naming.
2. Use `json/scenes_world_of_steam.json` to build or block scenes through the Blender/Unreal side of the pipeline.
3. Use `storyboard/world_of_steam_prompts.md` to generate concept art, storyboard plates, scene references, and ComfyUI reference images.
4. Use the existing UE5 to ComfyUI workflow for stylized render passes once placeholder or final assets exist.

No generated models, rendered frames, or source PDFs are included in this first pass.
