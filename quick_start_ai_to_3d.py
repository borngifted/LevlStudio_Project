#!/usr/bin/env python3
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
    print("\n🪑 Generating van interior components...")
    interior_parts = ["seats", "dashboard", "door_panels"]
    
    for part in interior_parts:
        part_result = pipeline.generate_concept_image(
            prompt=f"Van interior {part}, isometric view, clean background, isolated component for 3D modeling",
            asset_name=f"van_{part}"
        )
        if part_result.get("success"):
            print(f"✅ {part}: {part_result['image_path']}")
    
    print("\n🎯 Next steps:")
    print("1. Take the generated images to Tripo3D, Meshy, or Hunyuan 3D")
    print("2. Download the 3D models as GLB files")
    print("3. Run cleanup: python3 ai_to_3d_pipeline.py --step cleanup --model-path your_model.glb --name asset_name")
    print("4. Import FBX files into Unreal Engine")

if __name__ == "__main__":
    main()
