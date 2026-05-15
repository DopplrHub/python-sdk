from dopplrhub import DopplrHub

api = DopplrHub(
    api_key="YOUR_API_KEY",
    base_url="https://api.dopplrhub.com/api/v1",
)

rates = api.utilities.currency_rates("USD")
print(dict(list(rates["rates"].items())[:5]))

(api.tools.ocr("./input.pdf", "ocr-docx", language="eng")
    .wait()
    .download("./input.docx"))

(api.tools.pdf_compress("./packet.pdf", "screen")
    .wait()
    .download("./packet-compressed.pdf"))

(api.tools.image_resize("./hero.png", width=1920, height=1080, fit="cover", output_format="webp")
    .wait()
    .download("./hero.webp"))

(api.tools.video_trim("./clip.mp4", start_time=3, end_time=12, output_format="mp4")
    .wait()
    .download("./clip-trimmed.mp4"))

api.tools.ada("./brochure.pdf").download("./brochure-ada-report.pdf")
api.tools.ats(
    "./resume.pdf",
    "Senior Python engineer with API design experience",
    industry="technology",
).download("./resume-optimized.docx")
