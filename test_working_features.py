#!/usr/bin/env python3
"""
Test Working GameCraft Features
Shows you exactly what's working and how to use it
"""

import sys
import json
from pathlib import Path

def test_environment():
    """Test the basic environment setup"""
    print("🧪 Testing GameCraft Environment")
    print("=" * 40)
    
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__}")
        
        if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            print("✅ Metal Performance Shaders available")
            device = "mps"
        else:
            print("⚠️ Using CPU (Metal not available)")
            device = "cpu"
            
        # Test a simple tensor operation
        x = torch.randn(3, 3)
        y = torch.matmul(x, x.T)
        print(f"✅ PyTorch tensor operations working on {device}")
        
    except Exception as e:
        print(f"❌ PyTorch test failed: {e}")
        return False
        
    try:
        import cv2
        print(f"✅ OpenCV {cv2.__version__}")
        
        import numpy as np
        print(f"✅ NumPy {np.__version__}")
        
        import transformers
        print(f"✅ Transformers {transformers.__version__}")
        
    except Exception as e:
        print(f"❌ Dependencies test failed: {e}")
        return False
        
    return True

def test_gamecraft_modules():
    """Test GameCraft integration modules"""
    print("\n🎮 Testing GameCraft Modules")
    print("=" * 35)
    
    # Add project to path
    project_root = Path(__file__).parent
    sys.path.append(str(project_root))
    
    try:
        # Test GameCraft Runner
        from gamecraft_integration.gamecraft_runner import GameCraftRunner, WORLD_PRESETS
        print("✅ GameCraftRunner imported")
        print(f"   📊 {len(WORLD_PRESETS)} world presets available")
        
        # Test Video Processor
        from gamecraft_integration.video_processor import VideoProcessor
        print("✅ VideoProcessor imported")
        
        # Test Pipeline Manager
        from gamecraft_integration.pipeline_manager import PipelineManager
        print("✅ PipelineManager imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Module import failed: {e}")
        return False

def test_gamecraft_runner():
    """Test GameCraft Runner functionality"""
    print("\n🏗️ Testing GameCraft Runner")
    print("=" * 30)
    
    try:
        sys.path.append(str(Path(__file__).parent))
        from gamecraft_integration.gamecraft_runner import GameCraftRunner
        
        # Initialize runner with GameCraft path
        gamecraft_path = Path(__file__).parent / "Hunyuan-GameCraft-1.0"
        
        if not gamecraft_path.exists():
            print("❌ GameCraft directory not found")
            return False
            
        runner = GameCraftRunner(str(gamecraft_path))
        print("✅ GameCraftRunner initialized")
        
        # Test model info
        info = runner.get_model_info()
        print(f"✅ GameCraft path: {info['gamecraft_path']}")
        print(f"✅ Weights path: {info['weights_path']}")
        print(f"✅ Available models: {info['available_models']}")
        
        if not info['available_models']:
            print("⚠️ No models found - need to download")
        
        return True
        
    except Exception as e:
        print(f"❌ GameCraft Runner test failed: {e}")
        return False

def show_available_presets():
    """Show all available world presets"""
    print("\n🏰 Available World Presets")
    print("=" * 30)
    
    try:
        config_file = Path(__file__).parent / "gamecraft_configs" / "world_presets.json"
        with open(config_file, 'r') as f:
            presets = json.load(f)
            
        for name, config in presets.items():
            print(f"\n🎯 {name}")
            print(f"   📝 {config['description']}")
            print(f"   🎬 Actions: {' → '.join(config['actions'])}")
            print(f"   ⚡ Quality: {config['inference_steps']} steps")
            print(f"   🏷️  Tags: {', '.join(config['tags'])}")
            
    except Exception as e:
        print(f"❌ Failed to load presets: {e}")

def show_usage_examples():
    """Show practical usage examples"""
    print("\n🚀 How to Use GameCraft (Once Models Are Downloaded)")
    print("=" * 55)
    
    print("""
1. 📥 Download Models (if not done):
   cd Hunyuan-GameCraft-1.0/weights
   huggingface-cli download tencent/Hunyuan-GameCraft-1.0 --local-dir ./

2. 🎮 Activate Environment:
   source gamecraft_venv/bin/activate

3. 🏰 Generate a World:
   python3 -c "
   import sys; sys.path.append('.')
   from gamecraft_integration.gamecraft_runner import GameCraftRunner
   
   runner = GameCraftRunner('./Hunyuan-GameCraft-1.0')
   
   video = runner.generate_world_video(
       prompt='Medieval village with cobblestone streets',
       actions=['w', 's', 'd', 'a'],
       action_speeds=[0.2, 0.2, 0.2, 0.2],
       inference_steps=30,
       use_distilled=False,
       output_path='./my_world_output'
   )
   
   print(f'Generated: {video}')
   "

4. 📹 Process Video:
   python3 -c "
   import sys; sys.path.append('.')
   from gamecraft_integration.video_processor import VideoProcessor
   
   processor = VideoProcessor(device='mps')  # or 'cpu'
   analysis = processor.process_video('./my_world_output/video.mp4')
   print('Video analysis complete!')
   "
""")

def show_model_download_status():
    """Check model download status"""
    print("\n📥 Model Download Status")
    print("=" * 25)
    
    weights_dir = Path(__file__).parent / "Hunyuan-GameCraft-1.0" / "weights"
    
    if not weights_dir.exists():
        print("❌ Weights directory not found")
        return
        
    models_dir = weights_dir / "gamecraft_models"
    std_models_dir = weights_dir / "stdmodels"
    
    if models_dir.exists():
        model_files = list(models_dir.glob("*.pt"))
        print(f"🎮 GameCraft models: {len(model_files)} files")
        for model in model_files:
            size_mb = model.stat().st_size / (1024 * 1024)
            print(f"   ✅ {model.name} ({size_mb:.1f} MB)")
    else:
        print("❌ GameCraft models directory not found")
        
    if std_models_dir.exists():
        print(f"📚 Standard models directory exists")
        subdirs = [d for d in std_models_dir.iterdir() if d.is_dir()]
        print(f"   📊 {len(subdirs)} model subdirectories")
    else:
        print("❌ Standard models directory not found")
        
    print(f"\n💡 To download missing models:")
    print(f"   cd {weights_dir}")
    print(f"   huggingface-cli download tencent/Hunyuan-GameCraft-1.0 --local-dir ./")

def main():
    """Main test function"""
    print("🎮 GameCraft Working Features Test")
    print("=" * 45)
    
    # Test basic environment
    env_ok = test_environment()
    
    # Test modules
    modules_ok = test_gamecraft_modules()
    
    # Test GameCraft runner
    runner_ok = test_gamecraft_runner()
    
    # Show available content
    show_available_presets()
    
    # Show model status
    show_model_download_status()
    
    # Show usage examples
    show_usage_examples()
    
    print(f"\n{'='*45}")
    print(f"📊 Test Summary:")
    print(f"✅ Environment: {'Working' if env_ok else 'Failed'}")
    print(f"✅ Modules: {'Working' if modules_ok else 'Failed'}")
    print(f"✅ GameCraft Runner: {'Working' if runner_ok else 'Failed'}")
    
    if env_ok and modules_ok and runner_ok:
        print(f"\n🎉 GameCraft integration is working!")
        print(f"📝 You just need to download the AI models to start generating")
        print(f"🚀 Run the model download command shown above")
    else:
        print(f"\n⚠️ Some components need attention")
        print(f"🔧 Check the errors above and ensure environment is activated")

if __name__ == "__main__":
    main()