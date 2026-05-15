from dopplrhub import DopplrHub

api = DopplrHub(
    api_key="YOUR_API_KEY",
    base_url="https://api.dopplrhub.com/api/v1",
)

api.tools.ada("./brochure.pdf").download("./brochure-ada-report.pdf")
