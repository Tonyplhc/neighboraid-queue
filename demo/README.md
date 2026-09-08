# Reproducible local demo video

Prepared artifact

- `neighboraid-queue-demo.mp4`
- 109 seconds (1:49)
- H.264 High profile, 1280x720, 30 fps, yuv420p
- Captioned; narration intentionally omitted
- Synthetic project data only
- No external actions or network publishing

Rebuild

Prerequisites: the project virtual environment installed with `.[dev]`, plus `ffmpeg` and `ffprobe` on PATH.

From the project root:

    .venv/Scripts/python.exe demo/render_demo.py

The renderer first runs the real packaged CLI and project tests. It then recreates the 11 PNG source slides and encodes them with one-second cross-fades.

Validate

    ffprobe -v error -select_streams v:0 -show_entries stream=index,codec_name,codec_long_name,profile,width,height,pix_fmt,r_frame_rate,avg_frame_rate,duration -show_entries format=format_name,duration,size,bit_rate -of json -o demo/ffprobe.json demo/neighboraid-queue-demo.mp4
    ffmpeg -v error -i demo/neighboraid-queue-demo.mp4 -f null -

Reproducibility/evidence files

- `render_demo.py`: complete renderer
- `slides/`: source frames
- `manifest.json`: scene timings and captured test/CLI evidence
- `cli-output.txt`: real CLI stdout captured during render
- `test-output.txt`: real pytest stdout captured during render
- `ffmpeg-command.txt`: exact generated encoding command
- `ffmpeg-render-log.txt`: encoder log
- `ffprobe.json`: probed stream/container metadata
- `contact-sheet.png`: review sheet of all 11 scenes
- `validation-frame.png`: extracted playable-video frame

The future public YouTube/Vimeo URL is deliberately absent until publication is explicitly authorized.
