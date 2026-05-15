from dopplrhub import DopplrHub

api = DopplrHub(
    api_key="YOUR_API_KEY",
    base_url="https://api.dopplrhub.com/api/v1",
)

api.tools.ats(
    "./resume.pdf",
    "Senior Python engineer with API design experience",
    industry="technology",
).download("./resume-optimized.docx")
