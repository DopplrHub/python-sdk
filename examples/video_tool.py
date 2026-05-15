from dopplrhub import DopplrHub

api = DopplrHub(
    api_key="YOUR_API_KEY",
    base_url="https://api.dopplrhub.com/api/v1",
)

(api.tools.video_trim("./clip.mp4", start_time=3, end_time=12, output_format="mp4")
    .wait()
    .download("./clip-trimmed.mp4"))
