# DopplrHub Python SDK

A Python SDK for the current DopplrHub public API, including generic conversions, tools, and utility endpoints.

## Install

```bash
pip install dopplrhub
```

For this local scaffold:

```bash
cd D:\AudioConverter\sdk\python
pip install -e .
```

If you want to distribute the SDK directly from the backend, this workspace will expose a zip bundle at `/api/sdk/python-sdk.zip`.

## Local file conversion

```python
from dopplrhub import DopplrHub

api = DopplrHub("YOUR_API_KEY", "https://api.dopplrhub.com/api/v1")

(api.start("./input.pdf", "jpg")
    .wait()
    .download("./input.jpg")
    .delete())
```

## Remote file conversion

```python
from dopplrhub import DopplrHub

api = DopplrHub("YOUR_API_KEY", "https://api.dopplrhub.com/api/v1")

(api.start_from_url("https://example.com/brochure.pdf", "png")
    .wait()
    .download("./brochure.png")
    .delete())
```

## Tools

```python
from dopplrhub import DopplrHub

api = DopplrHub("YOUR_API_KEY", "https://api.dopplrhub.com/api/v1")

(api.tools.ocr("./scan.pdf", "ocr-docx", language="eng")
    .wait()
    .download("./scan.docx"))

(api.tools.image_resize(
    "./hero.png",
    width=1920,
    height=1080,
    fit="cover",
    output_format="webp",
)
    .wait()
    .download("./hero.webp"))

(api.tools.pdf_compress("./packet.pdf", "screen")
    .wait()
    .download("./packet-compressed.pdf"))

(api.tools.video_trim("./clip.mp4", start_time=3, end_time=12, output_format="mp4")
    .wait()
    .download("./clip-trimmed.mp4"))

api.tools.ada("./brochure.pdf").download("./brochure-ada-report.pdf")
api.tools.ats(
    "./resume.pdf",
    "Senior Python engineer with API design experience",
    industry="technology",
).download("./resume-optimized.docx")

(api.tools.archive(["./a.txt", "./b.txt"], "zip", archive_name="documents")
    .wait()
    .download("./documents.zip"))

(api.tools.social_resize(
    "./hero.png",
    platform="instagram",
    selected_size_ids=["post-square", "story"],
    output_format="jpg",
)
    .wait()
    .download("./hero-instagram.zip"))

result = api.tools.ats_reexport(report, "modern", download_as="resume-modern.docx")
result.download("./resume-modern.docx")
```

Tool coverage in the Python SDK includes `ocr`, `pdf`, `image`, `video`, `ada`, `ats`, `ats_reexport`, `archive`, and `social_resize` on `api.tools`.

## Examples

- `examples/convert_local_file.py`
- `examples/convert_remote_file.py`
- `examples/ocr_tool.py`
- `examples/pdf_tool.py`
- `examples/image_tool.py`
- `examples/video_tool.py`
- `examples/ada_tool.py`
- `examples/ats_tool.py`
- `examples/tools_and_utilities.py`

## Utilities

```python
from dopplrhub import DopplrHub

api = DopplrHub("YOUR_API_KEY", "https://api.dopplrhub.com/api/v1")

formats = api.utilities.supported_formats()
rates = api.utilities.currency_rates("USD")
api.utilities.batch_download(["JOB_ID_1", "JOB_ID_2"], "./converted_files.zip")
```

## Important behavior note

`start_from_url()` currently downloads the remote resource first, then uploads it into DopplrHub.
It does not perform headless browser webpage rendering.
