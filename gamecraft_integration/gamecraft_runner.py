"""
GameCraft Runner - Interface for Hunyuan-GameCraft-1.0
Handles video generation with interactive controls
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Optional, Union
import logging

class GameCraftRunner:
    """Runner for Hunyuan-GameCraft-1.0 model"""
    
    def __init__(self, gamecraft_path: str, weights_path: str = None):
        """
        Initialize GameCraft runner
        
        Args:
            gamecraft_path: Path to Hunyuan-GameCraft-1.0 directory
            weights_path: Path to model weights (optional)
        """
        self.gamecraft_path = Path(gamecraft_path)
        self.weights_path = weights_path or self.gamecraft_path / "weights"
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Validate paths
        self._validate_installation()
        
    def _validate_installation(self):
        """Validate GameCraft installation"""
        required_files = [
            "hymm_sp/sample_batch.py",
            "requirements.txt"
        ]
        
        for file in required_files:
            if not (self.gamecraft_path / file).exists():
                raise FileNotFoundError(f"GameCraft file not found: {file}")
                
        # Check if weights exist
        model_path = self.weights_path / "gamecraft_models" / "mp_rank_00_model_states.pt"
        if not model_path.exists():
            self.logger.warning(f"Model weights not found at {model_path}")
            self.logger.info("Run: huggingface-cli download tencent/Hunyuan-GameCraft-1.0 --local-dir ./weights/")
    
    def generate_world_video(
        self,
        prompt: str,
        actions: List[str] = None,
        action_speeds: List[float] = None,
        image_path: str = None,
        video_size: tuple = (704, 1216),
        cfg_scale: float = 2.0,
        inference_steps: int = 50,
        seed: int = None,
        output_path: str = None,
        use_distilled: bool = False,
        use_fp8: bool = False,
        gpu_count: int = 1
    ) -> str:
        """
        Generate interactive game world video
        
        Args:
            prompt: Text description of the world
            actions: List of actions ['w', 's', 'a', 'd']
            action_speeds: Speed for each action (0-3)
            image_path: Optional starting image
            video_size: Output video dimensions
            cfg_scale: Classifier-free guidance scale
            inference_steps: Number of inference steps
            seed: Random seed
            output_path: Output directory
            use_distilled: Use faster distilled model
            use_fp8: Use FP8 optimization
            gpu_count: Number of GPUs to use
            
        Returns:
            Path to generated video
        """
        # Set defaults
        actions = actions or ['w', 's', 'd', 'a']
        action_speeds = action_speeds or [0.2] * len(actions)
        seed = seed or 250160
        output_path = output_path or str(self.gamecraft_path / "results")
        
        # Validate inputs
        if len(actions) != len(action_speeds):
            raise ValueError("actions and action_speeds must have same length")
            
        # Choose model
        model_file = "mp_rank_00_model_states_distill.pt" if use_distilled else "mp_rank_00_model_states.pt"
        checkpoint_path = self.weights_path / "gamecraft_models" / model_file
        
        if not checkpoint_path.exists():
            raise FileNotFoundError(f"Model checkpoint not found: {checkpoint_path}")
        
        # Build command
        cmd = self._build_inference_command(
            prompt=prompt,
            actions=actions,
            action_speeds=action_speeds,
            image_path=image_path,
            video_size=video_size,
            cfg_scale=cfg_scale,
            inference_steps=inference_steps,
            seed=seed,
            output_path=output_path,
            checkpoint_path=str(checkpoint_path),
            use_fp8=use_fp8,
            gpu_count=gpu_count,
            use_distilled=use_distilled
        )
        
        # Run inference
        self.logger.info(f"Starting GameCraft generation with prompt: {prompt}")
        self.logger.info(f"Actions: {' '.join(actions)}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.gamecraft_path),
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if result.returncode != 0:
                self.logger.error(f"GameCraft generation failed: {result.stderr}")
                raise RuntimeError(f"GameCraft generation failed: {result.stderr}")
                
            # Find generated video
            video_path = self._find_generated_video(output_path)
            self.logger.info(f"Video generated successfully: {video_path}")
            
            return video_path
            
        except subprocess.TimeoutExpired:
            self.logger.error("GameCraft generation timed out")
            raise RuntimeError("GameCraft generation timed out")
            
    def _build_inference_command(self, **kwargs) -> List[str]:
        """Build the torchrun command for inference"""
        
        # Base command
        cmd = [
            "torchrun",
            "--nnodes=1",
            f"--nproc_per_node={kwargs['gpu_count']}",
            "--master_port", "29605",
            "hymm_sp/sample_batch.py"
        ]
        
        # Add arguments
        if kwargs.get('image_path'):
            cmd.extend(["--image-path", kwargs['image_path']])
            cmd.append("--image-start")
            
        cmd.extend([
            "--prompt", kwargs['prompt'],
            "--add-pos-prompt", "Realistic, High-quality.",
            "--add-neg-prompt", "overexposed, low quality, deformation, bad composition, bad hands, bad teeth, bad eyes, bad limbs, distortion, blurring, text, subtitles, static, picture, black border.",
            "--ckpt", kwargs['checkpoint_path'],
            "--video-size", str(kwargs['video_size'][0]), str(kwargs['video_size'][1]),
            "--cfg-scale", str(kwargs['cfg_scale']),
            "--action-list"] + kwargs['actions'] + [
            "--action-speed-list"] + [str(s) for s in kwargs['action_speeds']] + [
            "--seed", str(kwargs['seed']),
            "--infer-steps", str(kwargs['inference_steps']),
            "--flow-shift-eval-video", "5.0",
            "--save-path", kwargs['output_path']
        ])
        
        # Optional flags
        if kwargs.get('use_fp8'):
            cmd.append("--use-fp8")
            
        # Distilled model settings
        if kwargs.get('use_distilled'):
            cmd.extend(["--cfg-scale", "1.0"])
            cmd.extend(["--infer-steps", "8"])
            
        return cmd
        
    def _find_generated_video(self, output_path: str) -> str:
        """Find the most recently generated video"""
        output_dir = Path(output_path)
        
        if not output_dir.exists():
            raise FileNotFoundError(f"Output directory not found: {output_path}")
            
        # Look for video files
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
        video_files = []
        
        for ext in video_extensions:
            video_files.extend(output_dir.glob(f"*{ext}"))
            
        if not video_files:
            raise FileNotFoundError("No video files found in output directory")
            
        # Return most recent
        latest_video = max(video_files, key=lambda f: f.stat().st_mtime)
        return str(latest_video)
        
    def get_model_info(self) -> Dict:
        """Get information about available models"""
        info = {
            'gamecraft_path': str(self.gamecraft_path),
            'weights_path': str(self.weights_path),
            'available_models': []
        }
        
        models_dir = self.weights_path / "gamecraft_models"
        if models_dir.exists():
            for model_file in models_dir.glob("*.pt"):
                info['available_models'].append(model_file.name)
                
        return info
        
    def create_world_preset(self, name: str, config: Dict) -> str:
        """Create a reusable world generation preset"""
        presets_dir = Path(__file__).parent.parent / "gamecraft_configs"
        presets_dir.mkdir(exist_ok=True)
        
        preset_file = presets_dir / f"{name}_preset.json"
        
        with open(preset_file, 'w') as f:
            json.dump(config, f, indent=2)
            
        return str(preset_file)
        
    def load_world_preset(self, name: str) -> Dict:
        """Load a world generation preset"""
        presets_dir = Path(__file__).parent.parent / "gamecraft_configs"
        preset_file = presets_dir / f"{name}_preset.json"
        
        if not preset_file.exists():
            raise FileNotFoundError(f"Preset not found: {name}")
            
        with open(preset_file, 'r') as f:
            return json.load(f)


# Preset configurations for common world types
WORLD_PRESETS = {
    'medieval_village': {
        'prompt': 'A charming medieval village with cobblestone streets, thatched-roof houses, and vibrant flower gardens under a bright blue sky',
        'actions': ['w', 's', 'd', 'a'],
        'action_speeds': [0.2, 0.2, 0.2, 0.2],
        'cfg_scale': 2.0,
        'inference_steps': 50
    },
    'futuristic_city': {
        'prompt': 'Futuristic city with neon lights, flying cars, towering skyscrapers, and holographic advertisements in a cyberpunk setting',
        'actions': ['w', 'w', 's', 's', 'd', 'd', 'a', 'a'],
        'action_speeds': [0.3, 0.3, 0.2, 0.2, 0.25, 0.25, 0.25, 0.25],
        'cfg_scale': 2.0,
        'inference_steps': 50
    },
    'mystical_forest': {
        'prompt': 'Mystical forest with glowing mushrooms, ancient trees, magical particles, and ethereal lighting filtering through the canopy',
        'actions': ['w', 'a', 'w', 'd', 's', 'd', 'w', 'a'],
        'action_speeds': [0.15, 0.15, 0.15, 0.15, 0.1, 0.15, 0.15, 0.15],
        'cfg_scale': 2.5,
        'inference_steps': 60
    },
    'desert_oasis': {
        'prompt': 'Desert oasis with palm trees, crystal clear water, ancient ruins, and golden sand dunes under a sunset sky',
        'actions': ['w', 's', 'w', 'a', 'd', 'w'],
        'action_speeds': [0.2, 0.2, 0.2, 0.3, 0.3, 0.2],
        'cfg_scale': 2.0,
        'inference_steps': 50
    }
}


if __name__ == "__main__":
    # Example usage
    gamecraft_path = "/path/to/Hunyuan-GameCraft-1.0"
    runner = GameCraftRunner(gamecraft_path)
    
    # Generate a medieval village
    video_path = runner.generate_world_video(
        prompt="A charming medieval village with cobblestone streets",
        actions=['w', 's', 'd', 'a'],
        action_speeds=[0.2, 0.2, 0.2, 0.2]
    )
    
    print(f"Generated video: {video_path}")