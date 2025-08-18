#!/usr/bin/env python3
"""
Quick GameCraft Demo
Shows the integration working and simulates what happens when models are ready
"""

import sys
import json
import time
from pathlib import Path

def check_environment():
    """Check if environment is ready"""
    print("🧪 Checking GameCraft Environment...")
    
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__}")
        
        if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            print("✅ Metal Performance Shaders available")
            device = "mps"
        else:
            device = "cpu"
            print("⚠️ Using CPU")
            
        return device
    except ImportError:
        print("❌ PyTorch not available")
        return None

def check_models():
    """Check model download status"""
    print("\n📥 Checking Model Status...")
    
    weights_dir = Path("Hunyuan-GameCraft-1.0/weights")
    models_dir = weights_dir / "gamecraft_models"
    
    main_model = models_dir / "mp_rank_00_model_states.pt"
    distill_model = models_dir / "mp_rank_00_model_states_distill.pt"
    
    models_ready = main_model.exists() and main_model.stat().st_size > 1000000000  # >1GB
    
    if models_ready:
        size_gb = main_model.stat().st_size / (1024**3)
        print(f"✅ Main model ready: {size_gb:.1f} GB")
        return True
    else:
        print("⚠️ Models still downloading or not ready")
        print("📊 Current status:")
        
        if main_model.exists():
            size_mb = main_model.stat().st_size / (1024**2)
            print(f"   📥 Main model: {size_mb:.1f} MB (downloading...)")
        else:
            print("   ⏳ Main model: Not started")
            
        if distill_model.exists():
            size_mb = distill_model.stat().st_size / (1024**2)
            print(f"   📥 Distilled model: {size_mb:.1f} MB (downloading...)")
        else:
            print("   ⏳ Distilled model: Not started")
            
        return False

def demo_integration():
    """Demo the GameCraft integration"""
    print("\n🎮 GameCraft Integration Demo")
    print("=" * 35)
    
    # Add project to path
    sys.path.append(str(Path(__file__).parent))
    
    try:
        from gamecraft_integration.gamecraft_runner import GameCraftRunner, WORLD_PRESETS
        
        # Initialize runner
        gamecraft_path = "./Hunyuan-GameCraft-1.0"
        runner = GameCraftRunner(gamecraft_path)
        
        print(f"✅ GameCraft Runner initialized")
        print(f"📁 GameCraft path: {runner.gamecraft_path}")
        
        # Show available presets
        print(f"\n🏰 Available World Presets ({len(WORLD_PRESETS)}):")
        for name, config in list(WORLD_PRESETS.items())[:3]:  # Show first 3
            print(f"   🎯 {name}: {config['description'][:50]}...")
            
        # Show what would happen when models are ready
        print(f"\n🚀 What happens when models are ready:")
        print(f"   1. Choose a world preset (e.g., 'medieval_village')")
        print(f"   2. GameCraft generates interactive video (704x1216, 25fps)")
        print(f"   3. Video shows explorable world with WASD controls")
        print(f"   4. Pipeline processes video for 3D reconstruction")
        print(f"   5. Exports to Unreal Engine compatible format")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration demo failed: {e}")
        return False

def simulate_generation():
    """Simulate what generation would look like"""
    print(f"\n🎬 Simulating World Generation...")
    print("=" * 40)
    
    # Simulate the process
    steps = [
        ("🎯 Loading world preset: medieval_village", 1),
        ("📝 Processing prompt: 'Medieval village with cobblestone streets'", 1),
        ("🎮 Setting up actions: [w, s, d, a]", 0.5),
        ("⚡ Initializing GameCraft model", 2),
        ("🔮 Generating frame 1/132 (action: w - forward)", 1),
        ("🔮 Generating frame 33/132 (action: s - backward)", 1),
        ("🔮 Generating frame 66/132 (action: d - right)", 1),
        ("🔮 Generating frame 99/132 (action: a - left)", 1),
        ("🔮 Generating frame 132/132 (complete)", 1),
        ("🎥 Saving video: 704x1216 @ 25fps", 1),
        ("📹 Video saved: ./gamecraft_outputs/medieval_village.mp4", 0.5),
        ("🔍 Analyzing video for 3D reconstruction", 1),
        ("🏗️ Extracting depth maps and object masks", 1),
        ("🎨 Creating 3D meshes and materials", 1),
        ("🎮 Exporting to Unreal Engine format", 1),
        ("✅ Complete! Ready to import into Unreal", 0.5)
    ]
    
    for step, delay in steps:
        print(f"   {step}")
        time.sleep(delay)
    
    print(f"\n🎉 Generation Complete!")
    print(f"📁 Output files:")
    print(f"   🎥 medieval_village.mp4 - Interactive game video")
    print(f"   📊 analysis_results.json - 3D reconstruction data")
    print(f"   🎮 unreal_assets/ - FBX meshes, materials, blueprints")

def show_next_steps():
    """Show what to do next"""
    print(f"\n📝 Next Steps:")
    print("=" * 15)
    
    models_ready = check_models()
    
    if models_ready:
        print(f"🎉 Models are ready! You can generate worlds now:")
        print(f"")
        print(f"# Activate environment")
        print(f"source gamecraft_venv/bin/activate")
        print(f"")
        print(f"# Generate a medieval village")
        print(f'python3 -c "')
        print(f'import sys; sys.path.append(\".\")')
        print(f'from gamecraft_integration.gamecraft_runner import GameCraftRunner')
        print(f'runner = GameCraftRunner(\"./Hunyuan-GameCraft-1.0\")')
        print(f'video = runner.generate_world_video(')
        print(f'    prompt=\"Medieval village with cobblestone streets\",')
        print(f'    actions=[\"w\", \"s\", \"d\", \"a\"],')
        print(f'    action_speeds=[0.2, 0.2, 0.2, 0.2],')
        print(f'    inference_steps=30,')
        print(f'    output_path=\"./my_world\"')
        print(f')')
        print(f'print(f\"Generated: {{video}}\")')
        print(f'"')
    else:
        print(f"⏳ Models are still downloading (this is normal - 30GB+ files)")
        print(f"")
        print(f"While waiting, you can:")
        print(f"1. Explore world presets: python3 demo_gamecraft.py --show-presets")
        print(f"2. Check download progress: ls -lah Hunyuan-GameCraft-1.0/weights/gamecraft_models/")
        print(f"3. Test integration: python3 test_working_features.py")
        print(f"")
        print(f"Download will resume automatically. Check back in 10-30 minutes.")

def main():
    """Main demo function"""
    print("🎮 Quick GameCraft Demo")
    print("=" * 25)
    
    # Check environment
    device = check_environment()
    if not device:
        print("❌ Environment not ready")
        return
    
    # Check models
    models_ready = check_models()
    
    # Demo integration
    integration_ok = demo_integration()
    
    if not integration_ok:
        print("❌ Integration failed")
        return
    
    # Show simulation if models aren't ready
    if not models_ready:
        print(f"\n💡 Since models are downloading, here's what generation looks like:")
        simulate_generation()
    
    # Show next steps
    show_next_steps()
    
    print(f"\n🎯 GameCraft Integration Ready!")
    print(f"📚 See demo_gamecraft.py for more options")

if __name__ == "__main__":
    main()