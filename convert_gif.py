import imageio_ffmpeg
import os
import subprocess

video_in = "/config/.gemini/antigravity/brain/97cb01e4-7e65-48ed-80fd-146d1a04dc8c/foodlensai_demo.webm"
gif_out = "/config/.gemini/antigravity/scratch/simple-agent/demo.gif"

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
print(f"Using ffmpeg at: {ffmpeg_exe}")

cmd = [
    ffmpeg_exe, "-y",
    "-i", video_in,
    "-vf", "fps=10,scale=800:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
    gif_out
]

subprocess.run(cmd, check=True)
print(f"Successfully converted to {gif_out}, size: {os.path.getsize(gif_out)} bytes")
