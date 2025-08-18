"""
Video Processor - Analyze GameCraft videos for 3D reconstruction
Extracts frames, depth, objects, and motion data
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging
import json
from dataclasses import dataclass, asdict
import torch
import torchvision.transforms as transforms
from PIL import Image

try:
    import transformers
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False

@dataclass
class FrameAnalysis:
    """Analysis data for a single frame"""
    frame_id: int
    timestamp: float
    depth_map: Optional[np.ndarray] = None
    object_masks: Optional[Dict] = None
    camera_motion: Optional[Dict] = None
    lighting_analysis: Optional[Dict] = None
    dominant_colors: Optional[List] = None

class VideoProcessor:
    """Process GameCraft videos for 3D scene reconstruction"""
    
    def __init__(self, device: str = "auto"):
        """
        Initialize video processor
        
        Args:
            device: Computing device ('cpu', 'cuda', 'auto')
        """
        # Setup device
        if device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize models
        self._init_models()
        
    def _init_models(self):
        """Initialize AI models for analysis"""
        self.models = {}
        
        # Depth estimation model
        try:
            from transformers import AutoProcessor, AutoModelForDepthEstimation
            self.models['depth'] = {
                'processor': AutoProcessor.from_pretrained("Intel/dpt-large"),
                'model': AutoModelForDepthEstimation.from_pretrained("Intel/dpt-large").to(self.device)
            }
            self.logger.info("Loaded depth estimation model")
        except Exception as e:
            self.logger.warning(f"Could not load depth model: {e}")
            
        # Object detection model
        if TRANSFORMERS_AVAILABLE:
            try:
                self.models['object_detection'] = pipeline(
                    "object-detection",
                    model="facebook/detr-resnet-50",
                    device=0 if self.device == "cuda" else -1
                )
                self.logger.info("Loaded object detection model")
            except Exception as e:
                self.logger.warning(f"Could not load object detection model: {e}")
                
        # MediaPipe for additional analysis
        if MEDIAPIPE_AVAILABLE:
            self.mp_drawing = mp.solutions.drawing_utils
            self.mp_pose = mp.solutions.pose
            self.mp_hands = mp.solutions.hands
            self.mp_face_mesh = mp.solutions.face_mesh
            
    def process_video(self, video_path: str, output_dir: str = None) -> Dict:
        """
        Process GameCraft video for 3D reconstruction
        
        Args:
            video_path: Path to GameCraft video
            output_dir: Output directory for analysis results
            
        Returns:
            Complete video analysis data
        """
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")
            
        # Setup output directory
        if output_dir is None:
            output_dir = video_path.parent / f"{video_path.stem}_analysis"
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True, parents=True)
        
        self.logger.info(f"Processing video: {video_path}")
        
        # Extract basic video info
        video_info = self._get_video_info(str(video_path))
        
        # Process frames
        frames_data = self._extract_and_analyze_frames(str(video_path), output_dir)
        
        # Analyze camera motion
        camera_motion = self._analyze_camera_motion(frames_data)
        
        # Create environment layout
        environment_layout = self._create_environment_layout(frames_data)
        
        # Compile results
        analysis_results = {
            'video_info': video_info,
            'frames': frames_data,
            'camera_motion': camera_motion,
            'environment_layout': environment_layout,
            'processing_metadata': {
                'device_used': self.device,
                'models_loaded': list(self.models.keys()),
                'output_directory': str(output_dir)
            }
        }
        
        # Save analysis results
        results_file = output_dir / "analysis_results.json"
        self._save_analysis_results(analysis_results, results_file)
        
        self.logger.info(f"Video analysis complete. Results saved to: {output_dir}")
        return analysis_results
        
    def _get_video_info(self, video_path: str) -> Dict:
        """Extract basic video information"""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")
            
        info = {
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'duration': None
        }
        
        if info['fps'] > 0:
            info['duration'] = info['frame_count'] / info['fps']
            
        cap.release()
        return info
        
    def _extract_and_analyze_frames(self, video_path: str, output_dir: Path) -> List[Dict]:
        """Extract frames and run analysis"""
        cap = cv2.VideoCapture(video_path)
        frames_data = []
        
        # Create subdirectories
        frames_dir = output_dir / "frames"
        depth_dir = output_dir / "depth_maps"
        frames_dir.mkdir(exist_ok=True)
        depth_dir.mkdir(exist_ok=True)
        
        frame_id = 0
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            timestamp = frame_id / fps if fps > 0 else frame_id
            
            # Save frame
            frame_file = frames_dir / f"frame_{frame_id:06d}.jpg"
            cv2.imwrite(str(frame_file), frame)
            
            # Analyze frame
            analysis = FrameAnalysis(
                frame_id=frame_id,
                timestamp=timestamp
            )
            
            # Depth estimation
            if 'depth' in self.models:
                depth_map = self._estimate_depth(frame)
                analysis.depth_map = depth_map
                
                # Save depth map
                depth_file = depth_dir / f"depth_{frame_id:06d}.npy"
                np.save(str(depth_file), depth_map)
                
            # Object detection
            if 'object_detection' in self.models:
                objects = self._detect_objects(frame)
                analysis.object_masks = objects
                
            # Color analysis
            analysis.dominant_colors = self._analyze_colors(frame)
            
            # Lighting analysis
            analysis.lighting_analysis = self._analyze_lighting(frame)
            
            frames_data.append(asdict(analysis))
            frame_id += 1
            
            if frame_id % 10 == 0:
                self.logger.info(f"Processed {frame_id} frames")
                
        cap.release()
        self.logger.info(f"Extracted and analyzed {frame_id} frames")
        return frames_data
        
    def _estimate_depth(self, frame: np.ndarray) -> np.ndarray:
        """Estimate depth map for frame"""
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(rgb_frame)
            
            # Process with depth model
            processor = self.models['depth']['processor']
            model = self.models['depth']['model']
            
            inputs = processor(images=image, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = model(**inputs)
                predicted_depth = outputs.predicted_depth
                
            # Convert to numpy
            depth = predicted_depth.squeeze().cpu().numpy()
            
            # Normalize depth map
            depth = (depth - depth.min()) / (depth.max() - depth.min())
            
            return depth
            
        except Exception as e:
            self.logger.warning(f"Depth estimation failed: {e}")
            return None
            
    def _detect_objects(self, frame: np.ndarray) -> Dict:
        """Detect objects in frame"""
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(rgb_frame)
            
            # Run object detection
            results = self.models['object_detection'](image)
            
            # Process results
            objects = {
                'detections': [],
                'count_by_label': {}
            }
            
            for detection in results:
                label = detection['label']
                score = detection['score']
                box = detection['box']
                
                if score > 0.5:  # Confidence threshold
                    objects['detections'].append({
                        'label': label,
                        'score': score,
                        'box': box
                    })
                    
                    if label in objects['count_by_label']:
                        objects['count_by_label'][label] += 1
                    else:
                        objects['count_by_label'][label] = 1
                        
            return objects
            
        except Exception as e:
            self.logger.warning(f"Object detection failed: {e}")
            return None
            
    def _analyze_colors(self, frame: np.ndarray, num_colors: int = 5) -> List[Dict]:
        """Analyze dominant colors in frame"""
        try:
            # Reshape frame for k-means
            data = frame.reshape((-1, 3))
            data = np.float32(data)
            
            # K-means clustering
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
            _, labels, centers = cv2.kmeans(data, num_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            # Calculate percentages
            unique_labels, counts = np.unique(labels, return_counts=True)
            total_pixels = len(labels)
            
            colors = []
            for i, center in enumerate(centers):
                if i in unique_labels:
                    percentage = (counts[unique_labels == i][0] / total_pixels) * 100
                    colors.append({
                        'color_bgr': center.astype(int).tolist(),
                        'color_rgb': center[::-1].astype(int).tolist(),  # BGR to RGB
                        'percentage': float(percentage)
                    })
                    
            # Sort by percentage
            colors.sort(key=lambda x: x['percentage'], reverse=True)
            return colors
            
        except Exception as e:
            self.logger.warning(f"Color analysis failed: {e}")
            return []
            
    def _analyze_lighting(self, frame: np.ndarray) -> Dict:
        """Analyze lighting conditions in frame"""
        try:
            # Convert to different color spaces
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            
            # Calculate lighting metrics
            brightness = np.mean(gray)
            contrast = np.std(gray)
            
            # HSV analysis
            hue_mean = np.mean(hsv[:,:,0])
            saturation_mean = np.mean(hsv[:,:,1])
            value_mean = np.mean(hsv[:,:,2])
            
            # LAB analysis (L channel is lightness)
            lightness = np.mean(lab[:,:,0])
            
            return {
                'brightness': float(brightness),
                'contrast': float(contrast),
                'lightness': float(lightness),
                'hue_mean': float(hue_mean),
                'saturation_mean': float(saturation_mean),
                'value_mean': float(value_mean),
                'is_dark': brightness < 50,
                'is_bright': brightness > 200,
                'is_high_contrast': contrast > 50
            }
            
        except Exception as e:
            self.logger.warning(f"Lighting analysis failed: {e}")
            return {}
            
    def _analyze_camera_motion(self, frames_data: List[Dict]) -> Dict:
        """Analyze camera motion throughout video"""
        try:
            motion_data = {
                'motion_vectors': [],
                'motion_magnitude': [],
                'motion_direction': [],
                'camera_path': [],
                'motion_summary': {}
            }
            
            # Simple motion analysis based on frame differences
            # This would be enhanced with optical flow in production
            
            for i, frame_data in enumerate(frames_data):
                if i > 0:
                    # Calculate motion metrics
                    # This is a placeholder - real implementation would use optical flow
                    motion_magnitude = abs(i - (len(frames_data) / 2)) / (len(frames_data) / 2)
                    motion_data['motion_magnitude'].append(motion_magnitude)
                    
            # Summary statistics
            if motion_data['motion_magnitude']:
                motion_data['motion_summary'] = {
                    'avg_motion': float(np.mean(motion_data['motion_magnitude'])),
                    'max_motion': float(np.max(motion_data['motion_magnitude'])),
                    'motion_variance': float(np.var(motion_data['motion_magnitude']))
                }
                
            return motion_data
            
        except Exception as e:
            self.logger.warning(f"Camera motion analysis failed: {e}")
            return {}
            
    def _create_environment_layout(self, frames_data: List[Dict]) -> Dict:
        """Create environment layout from frame analysis"""
        try:
            layout = {
                'scene_elements': {},
                'spatial_structure': {},
                'temporal_consistency': {},
                'reconstruction_hints': {}
            }
            
            # Analyze scene elements across frames
            all_objects = {}
            for frame_data in frames_data:
                if frame_data.get('object_masks') and frame_data['object_masks'].get('count_by_label'):
                    for label, count in frame_data['object_masks']['count_by_label'].items():
                        if label not in all_objects:
                            all_objects[label] = []
                        all_objects[label].append(count)
                        
            # Create scene elements summary
            layout['scene_elements'] = {
                label: {
                    'frequency': len(counts),
                    'avg_count': float(np.mean(counts)),
                    'max_count': int(np.max(counts))
                }
                for label, counts in all_objects.items()
            }
            
            # Add reconstruction hints
            layout['reconstruction_hints'] = {
                'has_depth_data': any(f.get('depth_map') is not None for f in frames_data),
                'has_object_data': any(f.get('object_masks') is not None for f in frames_data),
                'frame_count': len(frames_data),
                'suitable_for_3d': len(frames_data) > 10 and any(f.get('depth_map') is not None for f in frames_data)
            }
            
            return layout
            
        except Exception as e:
            self.logger.warning(f"Environment layout creation failed: {e}")
            return {}
            
    def _save_analysis_results(self, results: Dict, output_file: Path):
        """Save analysis results to JSON file"""
        try:
            # Convert numpy arrays to lists for JSON serialization
            serializable_results = self._make_json_serializable(results)
            
            with open(output_file, 'w') as f:
                json.dump(serializable_results, f, indent=2, default=str)
                
        except Exception as e:
            self.logger.error(f"Failed to save results: {e}")
            
    def _make_json_serializable(self, obj):
        """Convert numpy arrays and other non-serializable objects"""
        if isinstance(obj, dict):
            return {key: self._make_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif isinstance(obj, np.ndarray):
            return "numpy_array_removed_for_json"  # Arrays saved separately
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        else:
            return obj


if __name__ == "__main__":
    # Example usage
    processor = VideoProcessor()
    
    # Process a GameCraft video
    video_path = "path/to/gamecraft_video.mp4"
    results = processor.process_video(video_path)
    
    print("Video processing complete!")
    print(f"Processed {len(results['frames'])} frames")
    print(f"Environment elements: {list(results['environment_layout']['scene_elements'].keys())}")