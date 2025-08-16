WAN-F'N Depth+Pose+Canny Flicker-Free ComfyUI Workflow
=====================================================

This template uses THREE ControlNets blended together to remove flicker
when applying a style from a reference image across an entire video.

Included ControlNets:
---------------------
1. DepthAnything  → Generates a depth map for each frame
2. DWPose         → Detects body/pose positions
3. PyraCanny      → Captures edge structure

Main Steps:
-----------
1) Load your UE5 video (MP4) into the "LoadVideo" node
2) DepthAnything, DWPose, and PyraCanny all process the same frames
3) Their outputs are merged into one ControlNet guidance stream
4) Style image is loaded (can be your video’s first frame or any reference image)
5) WAN-F'N applies the style using ControlNet guidance for flicker-free results
6) Output is saved as MP4

How to Use:
-----------
1. Save `wanfn_depth_pose_canny_template.json` into your ComfyUI `workflows` folder
2. In ComfyUI, click **Menu → Load** and choose this workflow
3. Replace the placeholders:
   - `@@video_path@@` → Path to your UE5 export video (MP4)
   - `@@style_image_path@@` → Style image (PNG/JPG)
   - `@@output_dir@@` → Output directory for the processed video
4. Make sure you have DepthAnything, DWPose, PyraCanny, and WAN-F'N nodes installed
5. Hit RUN

Tips:
-----
- Use the first frame of your video as style reference for most consistent results
- Keep `strength` between 0.8–0.9 for best flicker reduction
- If you get node not found errors, check that your custom_nodes are installed properly

Required Custom Nodes:
----------------------
- ControlNet for ComfyUI
- DepthAnything for ComfyUI
- DWPose (OpenPose)
- PyraCanny
- WAN-F'N style transfer

Credits:
--------
Based on workflows popularized by goshnii AI and MDMZ on YouTube.
