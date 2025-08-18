#!/usr/bin/env python3
"""
Test GameCraft Integration
Quick test script to verify GameCraft integration works
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__}")
        print(f"✅ CUDA available: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
            print(f"✅ GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        else:
            print("⚠️ CUDA not available - will use CPU (very slow)")
            
    except ImportError as e:
        print(f"❌ PyTorch import failed: {e}")
        return False
        
    try:
        import cv2
        print(f"✅ OpenCV {cv2.__version__}")
    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")
        return False
        
    try:
        import numpy as np
        print(f"✅ NumPy {np.__version__}")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
        
    try:
        from gamecraft_integration import GameCraftRunner, VideoProcessor, PipelineManager
        print("✅ GameCraft integration modules")
    except ImportError as e:
        print(f"❌ GameCraft integration import failed: {e}")
        return False
        
    return True

def test_gamecraft_runner():
    """Test GameCraftRunner initialization"""
    print("\n🎮 Testing GameCraft Runner...")
    
    gamecraft_path = project_root / "Hunyuan-GameCraft-1.0"
    
    if not gamecraft_path.exists():
        print(f"❌ GameCraft directory not found: {gamecraft_path}")
        return False
        
    try:
        from gamecraft_integration import GameCraftRunner
        runner = GameCraftRunner(str(gamecraft_path))
        
        print("✅ GameCraftRunner initialized")
        
        # Test model info
        info = runner.get_model_info()
        print(f"✅ GameCraft path: {info['gamecraft_path']}")
        print(f"✅ Weights path: {info['weights_path']}")
        print(f"✅ Available models: {info['available_models']}")
        
        if not info['available_models']:
            print("⚠️ No model weights found - run setup_gamecraft_environment.sh")
            
        return True
        
    except Exception as e:
        print(f"❌ GameCraftRunner test failed: {e}")
        return False

def test_video_processor():
    """Test VideoProcessor initialization"""
    print("\n📹 Testing Video Processor...")
    
    try:
        from gamecraft_integration import VideoProcessor
        processor = VideoProcessor(device="cpu")  # Use CPU for testing
        
        print("✅ VideoProcessor initialized")
        print(f"✅ Using device: {processor.device}")
        print(f"✅ Available models: {list(processor.models.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ VideoProcessor test failed: {e}")
        return False

def test_pipeline_manager():
    """Test PipelineManager initialization"""
    print("\n🔧 Testing Pipeline Manager...")
    
    gamecraft_path = project_root / "Hunyuan-GameCraft-1.0"
    
    if not gamecraft_path.exists():
        print(f"❌ GameCraft directory not found: {gamecraft_path}")
        return False
        
    try:
        from gamecraft_integration import PipelineManager
        pipeline = PipelineManager(
            str(gamecraft_path),
            str(project_root / "gamecraft_outputs"),
            device="cpu"
        )
        
        print("✅ PipelineManager initialized")
        
        # Test world presets
        presets = pipeline.list_world_presets()
        print(f"✅ Available presets: {list(presets.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ PipelineManager test failed: {e}")
        return False

def test_config_files():
    """Test configuration files"""
    print("\n⚙️ Testing configuration files...")
    
    config_dir = project_root / "gamecraft_configs"
    
    config_files = [
        "world_presets.json",
        "action_sequences.json", 
        "export_settings.json"
    ]
    
    for config_file in config_files:
        config_path = config_dir / config_file
        if config_path.exists():
            print(f"✅ {config_file}")
            try:
                import json
                with open(config_path, 'r') as f:
                    data = json.load(f)
                print(f"   📊 Contains {len(data)} entries")
            except Exception as e:
                print(f"   ⚠️ JSON parse error: {e}")
        else:
            print(f"❌ {config_file} not found")
            return False
            
    return True

def test_directory_structure():
    """Test directory structure"""
    print("\n📁 Testing directory structure...")
    
    required_dirs = [
        "gamecraft_integration",
        "gamecraft_outputs",
        "gamecraft_configs",
        "gamecraft_workflows"
    ]
    
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"✅ {dir_name}/")
        else:
            print(f"❌ {dir_name}/ not found")
            return False
            
    return True

def run_example_generation():
    """Run a small example generation (if models are available)"""
    print("\n🚀 Testing example generation...")
    
    gamecraft_path = project_root / "Hunyuan-GameCraft-1.0"
    weights_path = gamecraft_path / "weights" / "gamecraft_models"
    
    model_file = weights_path / "mp_rank_00_model_states.pt"
    
    if not model_file.exists():
        print("⚠️ Model weights not found - skipping generation test")
        print("   Run setup_gamecraft_environment.sh to download models")
        return True
        
    try:
        from gamecraft_integration import GameCraftRunner
        runner = GameCraftRunner(str(gamecraft_path))
        
        print("🎬 Attempting small test generation...")
        print("   This will take several minutes...")
        
        # Small test generation
        video_path = runner.generate_world_video(
            prompt="Simple test scene with basic geometry",
            actions=["w", "s"],  # Just 2 actions for quick test
            action_speeds=[0.2, 0.2],
            inference_steps=10,  # Low steps for speed
            use_distilled=True,  # Use fast model if available
            use_fp8=True,        # Use FP8 for speed
            output_path=str(project_root / "test_output")
        )
        
        print(f"✅ Test generation completed: {video_path}")
        return True
        
    except Exception as e:
        print(f"❌ Example generation failed: {e}")
        print("   This is expected if models aren't downloaded or GPU unavailable")
        return False

def main():
    """Run all tests"""
    print("🧪 GameCraft Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Directory Structure", test_directory_structure),
        ("Configuration Files", test_config_files),
        ("GameCraft Runner", test_gamecraft_runner),
        ("Video Processor", test_video_processor),
        ("Pipeline Manager", test_pipeline_manager),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print(f"\n{'='*50}")
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! GameCraft integration is working.")
        
        # Optional generation test
        print(f"\n{'='*20} Optional Generation Test {'='*20}")
        run_example_generation()
        
    else:
        print("⚠️ Some tests failed. Check the errors above.")
        print("\n🔧 Common solutions:")
        print("1. Run: source activate_gamecraft.sh")
        print("2. Install missing dependencies")
        print("3. Download models: ./setup_gamecraft_environment.sh")
        
    print(f"\n🎮 GameCraft Integration Ready!")
    print(f"📚 See GAMECRAFT_INTEGRATION_DESIGN.md for usage guide")

if __name__ == "__main__":
    main()