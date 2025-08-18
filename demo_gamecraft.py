#!/usr/bin/env python3
"""
GameCraft Demo Script
Shows how to use the GameCraft integration
"""

import sys
import json
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def show_help():
    """Show available commands and options"""
    print("🎮 GameCraft Integration Demo")
    print("=" * 50)
    
    print("\n📝 Available Commands:")
    print("  demo_gamecraft.py --show-presets    # Show world presets")
    print("  demo_gamecraft.py --show-actions    # Show action sequences") 
    print("  demo_gamecraft.py --show-examples   # Show usage examples")
    print("  demo_gamecraft.py --test-import     # Test basic imports")
    
    print("\n🌍 When Environment is Ready:")
    print("  python gamecraft_integration/pipeline_manager.py \\")
    print("    --gamecraft-path './Hunyuan-GameCraft-1.0' \\")
    print("    --prompt 'Your world description' \\")
    print("    --world-type 'medieval_village' \\")
    print("    --quality 'medium'")

def show_world_presets():
    """Show available world presets"""
    print("🏰 Available World Presets:")
    print("=" * 30)
    
    try:
        with open('gamecraft_configs/world_presets.json', 'r') as f:
            presets = json.load(f)
            
        for name, config in presets.items():
            print(f"\n🎯 {name}")
            print(f"   📝 {config['description']}")
            print(f"   🎬 Actions: {' → '.join(config['actions'])}")
            print(f"   ⚡ Steps: {config['inference_steps']}")
            print(f"   🏷️  Tags: {', '.join(config['tags'])}")
            
    except FileNotFoundError:
        print("❌ World presets file not found")

def show_action_sequences():
    """Show available action sequences"""
    print("🎮 Available Action Sequences:")
    print("=" * 35)
    
    try:
        with open('gamecraft_configs/action_sequences.json', 'r') as f:
            sequences = json.load(f)
            
        for category, actions in sequences.items():
            print(f"\n📂 {category.replace('_', ' ').title()}")
            for name, config in actions.items():
                print(f"   🎯 {name}: {config['description']}")
                print(f"      Actions: {' → '.join(config['actions'])}")
                print(f"      Duration: {config['duration_frames']} frames")
                
    except FileNotFoundError:
        print("❌ Action sequences file not found")

def show_usage_examples():
    """Show detailed usage examples"""
    print("🚀 GameCraft Usage Examples:")
    print("=" * 35)
    
    examples = [
        {
            "name": "Medieval Village",
            "command": """python gamecraft_integration/pipeline_manager.py \\
  --gamecraft-path "./Hunyuan-GameCraft-1.0" \\
  --prompt "Charming medieval village with cobblestone streets and market" \\
  --world-type "medieval_village" \\
  --quality "medium" \\
  --output-dir "./my_medieval_world" """,
            "description": "Generate a medieval village with automatic exploration"
        },
        {
            "name": "Custom Futuristic City", 
            "command": """python gamecraft_integration/pipeline_manager.py \\
  --gamecraft-path "./Hunyuan-GameCraft-1.0" \\
  --prompt "Neon-lit cyberpunk city with flying vehicles and holographic ads" \\
  --actions w w s s d d a a \\
  --action-speeds 0.3 0.3 0.2 0.2 0.25 0.25 0.25 0.25 \\
  --quality "high" \\
  --include-animations""",
            "description": "Custom futuristic city with specific camera movements"
        },
        {
            "name": "Quick Test Generation",
            "command": """python gamecraft_integration/pipeline_manager.py \\
  --gamecraft-path "./Hunyuan-GameCraft-1.0" \\
  --prompt "Simple test environment" \\
  --actions w s \\
  --action-speeds 0.2 0.2 \\
  --quality "low" """,
            "description": "Fast test generation with minimal settings"
        }
    ]
    
    for example in examples:
        print(f"\n🎯 {example['name']}")
        print(f"📝 {example['description']}")
        print(f"💻 Command:")
        print(f"{example['command']}")
        print("-" * 50)

def test_basic_import():
    """Test basic imports without dependencies"""
    print("🧪 Testing Basic Integration:")
    print("=" * 35)
    
    try:
        # Test file existence
        required_files = [
            'gamecraft_integration/__init__.py',
            'gamecraft_integration/gamecraft_runner.py', 
            'gamecraft_integration/video_processor.py',
            'gamecraft_integration/pipeline_manager.py'
        ]
        
        for file_path in required_files:
            if Path(file_path).exists():
                print(f"✅ {file_path}")
            else:
                print(f"❌ {file_path}")
                
        # Test config files
        config_files = [
            'gamecraft_configs/world_presets.json',
            'gamecraft_configs/action_sequences.json',
            'gamecraft_configs/export_settings.json'
        ]
        
        print(f"\n📋 Configuration Files:")
        for config_file in config_files:
            if Path(config_file).exists():
                print(f"✅ {config_file}")
                with open(config_file, 'r') as f:
                    data = json.load(f)
                print(f"   📊 Contains {len(data)} entries")
            else:
                print(f"❌ {config_file}")
                
        # Test GameCraft repo
        gamecraft_path = Path('Hunyuan-GameCraft-1.0')
        print(f"\n🎮 GameCraft Repository:")
        if gamecraft_path.exists():
            print(f"✅ GameCraft repository present")
            
            weights_path = gamecraft_path / 'weights'
            if weights_path.exists():
                print(f"✅ Weights directory exists")
            else:
                print(f"⚠️  Weights directory not found - models need download")
                
            scripts_path = gamecraft_path / 'scripts'
            if scripts_path.exists():
                scripts = list(scripts_path.glob('*.sh'))
                print(f"✅ Found {len(scripts)} example scripts")
            else:
                print(f"❌ Scripts directory not found")
        else:
            print(f"❌ GameCraft repository not found")
            
        print(f"\n🎯 Integration Status: Structure Ready!")
        print(f"📝 Next: Run setup_gamecraft_environment.sh to install dependencies")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

def main():
    """Main demo function"""
    if len(sys.argv) < 2:
        show_help()
        return
        
    command = sys.argv[1]
    
    if command == '--show-presets':
        show_world_presets()
    elif command == '--show-actions':
        show_action_sequences()
    elif command == '--show-examples':
        show_usage_examples()
    elif command == '--test-import':
        test_basic_import()
    elif command == '--help':
        show_help()
    else:
        print(f"❌ Unknown command: {command}")
        show_help()

if __name__ == "__main__":
    main()