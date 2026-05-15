from dopplrhub import DopplrHub

api = DopplrHub(
    api_key="YOUR_API_KEY",
    base_url="https://api.dopplrhub.com/api/v1",
)

(api.tools.image_resize(
    "./hero.png",
    width=1920,
    height=1080,
    fit="cover",
    output_format="webp",
)
    .wait()
    .download("./hero.webp"))
