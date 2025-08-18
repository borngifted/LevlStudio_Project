"""
Pipeline Manager - Complete GameCraft to Unreal Engine workflow
Orchestrates the entire AI world building pipeline
"""

import argparse
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
import logging

from .gamecraft_runner import GameCraftRunner, WORLD_PRESETS
from .video_processor import VideoProcessor
# from .scene_reconstructor import SceneReconstructor
# from .unreal_exporter import UnrealExporter

class PipelineManager:
    """Manages complete GameCraft to Unreal Engine pipeline"""
    
    def __init__(
        self,
        gamecraft_path: str,
        output_base_dir: str = None,
        device: str = "auto"
    ):
        """
        Initialize pipeline manager
        
        Args:
            gamecraft_path: Path to Hunyuan-GameCraft-1.0 directory
            output_base_dir: Base directory for all outputs
            device: Computing device ('cpu', 'cuda', 'auto')
        """
        self.gamecraft_path = Path(gamecraft_path)
        self.output_base_dir = Path(output_base_dir) if output_base_dir else Path.cwd() / "gamecraft_outputs"
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.gamecraft_runner = GameCraftRunner(str(self.gamecraft_path))
        self.video_processor = VideoProcessor(device=device)
        # self.scene_reconstructor = SceneReconstructor()
        # self.unreal_exporter = UnrealExporter()
        
        # Create output directories
        self.output_base_dir.mkdir(exist_ok=True, parents=True)
        
    def run_complete_pipeline(
        self,
        prompt: str,
        world_type: str = "custom",
        actions: List[str] = None,
        action_speeds: List[float] = None,
        output_format: str = "unreal",
        quality: str = "medium",
        include_animations: bool = False,
        pipeline_name: str = None
    ) -> Dict:
        """
        Run complete pipeline from prompt to Unreal assets
        
        Args:
            prompt: World description
            world_type: Preset world type or 'custom'
            actions: Custom action sequence
            action_speeds: Custom action speeds
            output_format: Output format ('unreal', 'blender', 'generic')
            quality: Quality level ('low', 'medium', 'high', 'ultra')
            include_animations: Include camera animations
            pipeline_name: Name for this pipeline run
            
        Returns:
            Pipeline results with all output paths
        """
        # Generate pipeline name if not provided
        if not pipeline_name:
            pipeline_name = f"world_{int(time.time())}"
            
        pipeline_dir = self.output_base_dir / pipeline_name
        pipeline_dir.mkdir(exist_ok=True)
        
        self.logger.info(f"Starting complete pipeline: {pipeline_name}")
        self.logger.info(f"Prompt: {prompt}")
        
        results = {
            'pipeline_name': pipeline_name,
            'pipeline_dir': str(pipeline_dir),
            'config': {
                'prompt': prompt,
                'world_type': world_type,
                'quality': quality,
                'output_format': output_format,
                'include_animations': include_animations
            },
            'stages': {},
            'final_outputs': {},
            'timing': {}
        }
        
        try:
            # Stage 1: GameCraft Video Generation
            self.logger.info("Stage 1: Generating GameCraft video...")
            stage1_start = time.time()
            
            video_path = self._run_gamecraft_generation(
                prompt, world_type, actions, action_speeds, 
                quality, pipeline_dir
            )
            
            results['stages']['gamecraft_generation'] = {
                'status': 'completed',
                'output': video_path,
                'duration': time.time() - stage1_start
            }
            
            # Stage 2: Video Processing and Analysis
            self.logger.info("Stage 2: Processing video for 3D reconstruction...")
            stage2_start = time.time()
            
            analysis_results = self._run_video_processing(
                video_path, pipeline_dir
            )
            
            results['stages']['video_processing'] = {
                'status': 'completed',
                'output': analysis_results,
                'duration': time.time() - stage2_start
            }
            
            # Stage 3: 3D Scene Reconstruction (Placeholder)
            self.logger.info("Stage 3: 3D scene reconstruction...")
            stage3_start = time.time()
            
            # TODO: Implement when scene_reconstructor is ready
            scene_data = self._run_scene_reconstruction(
                analysis_results, pipeline_dir, quality
            )
            
            results['stages']['scene_reconstruction'] = {
                'status': 'placeholder',
                'output': scene_data,
                'duration': time.time() - stage3_start
            }
            
            # Stage 4: Unreal Engine Export (Placeholder)
            self.logger.info("Stage 4: Exporting to Unreal Engine...")
            stage4_start = time.time()
            
            # TODO: Implement when unreal_exporter is ready
            unreal_assets = self._run_unreal_export(
                scene_data, output_format, pipeline_dir, include_animations
            )
            
            results['stages']['unreal_export'] = {
                'status': 'placeholder',
                'output': unreal_assets,
                'duration': time.time() - stage4_start
            }
            
            # Compile final outputs
            results['final_outputs'] = {
                'original_video': video_path,
                'analysis_data': analysis_results['output_directory'],
                'unreal_assets': unreal_assets,
                'pipeline_report': str(pipeline_dir / 'pipeline_report.json')
            }
            
            # Save pipeline report
            self._save_pipeline_report(results, pipeline_dir / 'pipeline_report.json')
            
            self.logger.info(f"Pipeline completed successfully: {pipeline_name}")
            return results
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}")
            results['status'] = 'failed'
            results['error'] = str(e)
            return results
            
    def _run_gamecraft_generation(
        self,
        prompt: str,
        world_type: str,
        actions: List[str],
        action_speeds: List[float],
        quality: str,
        pipeline_dir: Path
    ) -> str:
        """Run GameCraft video generation"""
        
        # Use preset if specified
        if world_type != "custom" and world_type in WORLD_PRESETS:
            preset = WORLD_PRESETS[world_type]
            if not actions:
                actions = preset['actions']
            if not action_speeds:
                action_speeds = preset['action_speeds']
                
        # Set quality parameters
        quality_settings = {
            'low': {'inference_steps': 20, 'use_distilled': True, 'use_fp8': True},
            'medium': {'inference_steps': 30, 'use_distilled': False, 'use_fp8': True},
            'high': {'inference_steps': 50, 'use_distilled': False, 'use_fp8': False},
            'ultra': {'inference_steps': 80, 'use_distilled': False, 'use_fp8': False}
        }
        
        settings = quality_settings.get(quality, quality_settings['medium'])
        
        # Generate video
        video_path = self.gamecraft_runner.generate_world_video(
            prompt=prompt,
            actions=actions or ['w', 's', 'd', 'a'],
            action_speeds=action_speeds or [0.2, 0.2, 0.2, 0.2],
            output_path=str(pipeline_dir / "gamecraft_video"),
            **settings
        )
        
        return video_path
        
    def _run_video_processing(self, video_path: str, pipeline_dir: Path) -> Dict:
        """Run video processing and analysis"""
        
        analysis_dir = pipeline_dir / "video_analysis"
        analysis_results = self.video_processor.process_video(
            video_path, str(analysis_dir)
        )
        
        return analysis_results
        
    def _run_scene_reconstruction(
        self, 
        analysis_results: Dict, 
        pipeline_dir: Path, 
        quality: str
    ) -> Dict:
        """Run 3D scene reconstruction (placeholder)"""
        
        # This is a placeholder until SceneReconstructor is implemented
        reconstruction_dir = pipeline_dir / "scene_reconstruction"
        reconstruction_dir.mkdir(exist_ok=True)
        
        # Placeholder data
        scene_data = {
            'meshes': [],
            'materials': [],
            'lighting': {},
            'camera_path': [],
            'reconstruction_quality': quality,
            'output_directory': str(reconstruction_dir),
            'status': 'placeholder_implementation'
        }
        
        # Save placeholder data
        with open(reconstruction_dir / 'scene_data.json', 'w') as f:
            json.dump(scene_data, f, indent=2)
            
        return scene_data
        
    def _run_unreal_export(
        self,
        scene_data: Dict,
        output_format: str,
        pipeline_dir: Path,
        include_animations: bool
    ) -> Dict:
        """Run Unreal Engine export (placeholder)"""
        
        # This is a placeholder until UnrealExporter is implemented
        export_dir = pipeline_dir / "unreal_export"
        export_dir.mkdir(exist_ok=True)
        
        # Placeholder data
        unreal_assets = {
            'meshes': [],
            'materials': [],
            'blueprints': [],
            'animations': [] if include_animations else None,
            'level_file': str(export_dir / 'GameCraftLevel.umap'),
            'datasmith_file': str(export_dir / 'GameCraftScene.udatasmith'),
            'output_directory': str(export_dir),
            'status': 'placeholder_implementation'
        }
        
        # Save placeholder data
        with open(export_dir / 'unreal_assets.json', 'w') as f:
            json.dump(unreal_assets, f, indent=2, default=str)
            
        return unreal_assets
        
    def _save_pipeline_report(self, results: Dict, report_path: Path):
        """Save complete pipeline report"""
        try:
            with open(report_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Failed to save pipeline report: {e}")
            
    def list_world_presets(self) -> Dict:
        """List available world presets"""
        return WORLD_PRESETS
        
    def create_custom_preset(self, name: str, config: Dict) -> str:
        """Create a custom world preset"""
        return self.gamecraft_runner.create_world_preset(name, config)
        
    def get_pipeline_status(self, pipeline_name: str) -> Dict:
        """Get status of a pipeline run"""
        pipeline_dir = self.output_base_dir / pipeline_name
        report_file = pipeline_dir / 'pipeline_report.json'
        
        if not report_file.exists():
            return {'status': 'not_found'}
            
        try:
            with open(report_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            return {'status': 'error', 'error': str(e)}


def main():
    """Command-line interface for pipeline manager"""
    parser = argparse.ArgumentParser(description="GameCraft to Unreal Engine Pipeline")
    
    # Required arguments
    parser.add_argument("--gamecraft-path", required=True,
                       help="Path to Hunyuan-GameCraft-1.0 directory")
    parser.add_argument("--prompt", required=True,
                       help="Description of the world to generate")
    
    # Optional arguments
    parser.add_argument("--world-type", default="custom",
                       choices=list(WORLD_PRESETS.keys()) + ["custom"],
                       help="Preset world type")
    parser.add_argument("--actions", nargs="+", 
                       help="Custom action sequence (w s a d)")
    parser.add_argument("--action-speeds", nargs="+", type=float,
                       help="Action speeds (0.0-3.0)")
    parser.add_argument("--output-format", default="unreal",
                       choices=["unreal", "blender", "generic"],
                       help="Output format")
    parser.add_argument("--quality", default="medium",
                       choices=["low", "medium", "high", "ultra"],
                       help="Generation quality")
    parser.add_argument("--include-animations", action="store_true",
                       help="Include camera animations")
    parser.add_argument("--output-dir", 
                       help="Output directory")
    parser.add_argument("--pipeline-name",
                       help="Custom name for pipeline run")
    
    args = parser.parse_args()
    
    # Initialize pipeline manager
    pipeline_manager = PipelineManager(
        gamecraft_path=args.gamecraft_path,
        output_base_dir=args.output_dir
    )
    
    # Run pipeline
    results = pipeline_manager.run_complete_pipeline(
        prompt=args.prompt,
        world_type=args.world_type,
        actions=args.actions,
        action_speeds=args.action_speeds,
        output_format=args.output_format,
        quality=args.quality,
        include_animations=args.include_animations,
        pipeline_name=args.pipeline_name
    )
    
    # Print results
    if results.get('status') == 'failed':
        print(f"Pipeline failed: {results.get('error')}")
        return 1
    else:
        print("Pipeline completed successfully!")
        print(f"Pipeline name: {results['pipeline_name']}")
        print(f"Output directory: {results['pipeline_dir']}")
        if 'final_outputs' in results:
            print(f"Generated video: {results['final_outputs']['original_video']}")
            print(f"Analysis data: {results['final_outputs']['analysis_data']}")
        return 0


if __name__ == "__main__":
    exit(main())