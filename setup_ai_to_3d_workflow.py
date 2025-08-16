#!/usr/bin/env python3
"""
Setup script for AI-to-3D workflow
Installs dependencies and creates example workflows
"""

import subprocess
import sys
import os
from pathlib import Path

def install_dependencies():
    """Install required Python packages"""
    packages = [
        "openai>=1.0.0",
        "pillow>=9.0.0", 
        "opencv-python>=4.8.0",
        "requests>=2.28.0",
        "numpy>=1.24.0"
    ]
    
    print("📦 Installing AI-to-3D pipeline dependencies...")
    
    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to install {package}: {e}")
    
    print("✅ Dependencies installed!")

def create_example_workflows():
    """Create example workflow files"""
    
    # Van generation example (from the video)
    van_workflow = {
        "name": "delivery_van",
        "prompt": "White delivery van, side view, clean background, suitable for 3D modeling. Modern commercial vehicle with sliding door, simple design, well-lit, isometric perspective.",
        "steps": [
            "Generate concept image with AI",
            "Clean up in Photoshop/GIMP", 
            "Convert to 3D with Hunyuan/Tripo3D",
            "Clean mesh in Blender",
            "Retopology with Trio Studio",
            "Export FBX for Unreal Engine"
        ]
    }
    
    # Van interior parts
    van_interior_workflow = {
        "name": "van_interior_seats",
        "prompt": "Van interior seats, dashboard, and door panels, isometric view, clean background, separated components for 3D modeling",
        "parts": ["seats", "dashboard", "door_panels", "steering_wheel"]
    }
    
    # Create workflow directory
    workflow_dir = Path("ai_workflows")
    workflow_dir.mkdir(exist_ok=True)
    
    # Save examples
    import json
    
    with open(workflow_dir / "van_example.json", "w") as f:
        json.dump(van_workflow, f, indent=2)
    
    with open(workflow_dir / "van_interior_example.json", "w") as f:
        json.dump(van_interior_workflow, f, indent=2)
    
    print("✅ Example workflows created in ai_workflows/")

def create_quick_start_script():
    """Create a quick start script for the workflow"""
    
    quick_start = '''#!/usr/bin/env python3
"""
Quick start for AI-to-3D workflow
Example: Generate a van like in the video
"""

import os
from ai_to_3d_pipeline import AITo3DPipeline

def main():
    # Set your OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Please set your OPENAI_API_KEY environment variable")
        print("   export OPENAI_API_KEY='your-key-here'")
        return
    
    pipeline = AITo3DPipeline()
    
    # Example 1: Generate a delivery van (like in the video)
    print("🚐 Generating delivery van...")
    van_result = pipeline.full_pipeline(
        prompt="White delivery van, side view, clean white background, modern commercial vehicle with sliding door, well-lit for 3D modeling reference",
        asset_name="delivery_van"
    )
    
    print("Van generation result:")
    print(f"✅ Concept image: {van_result['steps']['1_concept_image'].get('image_path', 'Failed')}")
    print(f"✅ Cleaned image: {van_result['steps']['2_image_cleanup'].get('cleaned_image_path', 'Failed')}")
    print("✅ 3D conversion: Use online service with the generated image")
    
    # Example 2: Generate van interior components
    print("\\n🪑 Generating van interior components...")
    interior_parts = ["seats", "dashboard", "door_panels"]
    
    for part in interior_parts:
        part_result = pipeline.generate_concept_image(
            prompt=f"Van interior {part}, isometric view, clean background, isolated component for 3D modeling",
            asset_name=f"van_{part}"
        )
        if part_result.get("success"):
            print(f"✅ {part}: {part_result['image_path']}")
    
    print("\\n🎯 Next steps:")
    print("1. Take the generated images to Tripo3D, Meshy, or Hunyuan 3D")
    print("2. Download the 3D models as GLB files")
    print("3. Run cleanup: python3 ai_to_3d_pipeline.py --step cleanup --model-path your_model.glb --name asset_name")
    print("4. Import FBX files into Unreal Engine")

if __name__ == "__main__":
    main()
'''
    
    with open("quick_start_ai_to_3d.py", "w") as f:
        f.write(quick_start)
    
    # Make executable
    os.chmod("quick_start_ai_to_3d.py", 0o755)
    
    print("✅ Quick start script created: quick_start_ai_to_3d.py")

def setup_environment_instructions():
    """Print setup instructions for external tools"""
    
    instructions = """
🛠️  AI-to-3D Workflow Setup Complete!

📋 Required External Tools (install separately):

1. 🎨 OpenAI API Key:
   - Get key from: https://platform.openai.com/api-keys
   - Set environment variable: export OPENAI_API_KEY='your-key-here'

2. 🎯 3D Generation Services (choose one):
   - Tripo3D: https://www.tripo3d.ai/ (recommended, free tier)
   - Meshy: https://www.meshy.ai/
   - Luma Genie: https://lumalabs.ai/genie
   - Hunyuan 3D: Install via Pinocchio or manual setup

3. 🎭 Blender (for cleanup):
   - Download: https://www.blender.org/download/
   - Add to PATH or use: /Applications/Blender.app/Contents/MacOS/Blender

4. ⚙️ Trio Studio (for retopology):
   - Download from official website
   - Alternative: Use Blender's remesh modifier

🚀 Quick Start:
   python3 quick_start_ai_to_3d.py

📖 Full Pipeline:
   python3 ai_to_3d_pipeline.py --prompt "your description" --name "asset_name"

💡 Tips:
   - Use isometric/orthographic views for better 3D conversion
   - Keep backgrounds clean and simple
   - Generate multiple angles for complex objects
   - Always clean up meshes before importing to UE5
"""
    
    print(instructions)

def main():
    print("🎬 Setting up AI-to-3D Workflow for LevlStudio")
    print("=" * 50)
    
    install_dependencies()
    create_example_workflows()
    create_quick_start_script()
    setup_environment_instructions()
    
    print("🎉 Setup complete! Ready to generate 3D assets from AI.")

if __name__ == "__main__":
    main()