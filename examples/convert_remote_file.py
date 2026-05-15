from dopplrhub import DopplrHub

api = DopplrHub(
    api_key="YOUR_API_KEY",
    base_url="https://api.dopplrhub.com/api/v1",
)

(api.start_from_url("https://example.com/sample.pdf", "png")
    .wait()
    .download("./sample.png")
    .delete())
