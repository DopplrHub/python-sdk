from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import quote, urlparse

import requests

from .exceptions import DopplrHubError
from .models import ConversionJob, ImmediateResult, UploadedFile


class UtilitiesClient:
    def __init__(self, client: "DopplrHub") -> None:
        self._client = client

    def supported_formats(self) -> dict[str, Any]:
        return self._client.request_json("GET", "/upload/formats")

    def currency_rates(self, base: str = "USD") -> dict[str, Any]:
        return self._client.request_json("GET", f"/tools/units/currency-rates?base={quote(base.upper())}")

    def batch_download(self, job_ids: list[str], target_path: str | Path) -> Path:
        if not job_ids:
            raise DopplrHubError("job_ids must be a non-empty list.")

        response = self._client.request(
            "POST",
            "/jobs/batch-download",
            json={"jobIds": list(job_ids)},
            headers={"Accept": "application/zip"},
        )
        self._client.raise_for_error(response)

        output = Path(target_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(response.content)
        return output


class ToolsClient:
    def __init__(self, client: "DopplrHub") -> None:
        self._client = client

    def pdf_merge(self, sources: list[Any], params: dict[str, Any] | None = None, **options: Any) -> ConversionJob:
        return self.pdf(sources, "merge", params, **options)

    def pdf_split(self, source: Any, ranges: str = "", **options: Any) -> ConversionJob:
        return self.pdf(source, "split", {"ranges": ranges}, **options)

    def pdf_compress(self, source: Any, quality: str = "medium", **options: Any) -> ConversionJob:
        return self.pdf(source, "compress", {"quality": quality}, **options)

    def pdf_rotate(self, source: Any, degrees: int = 90, pages: str = "all", **options: Any) -> ConversionJob:
        return self.pdf(source, "rotate", {"degrees": degrees, "pages": pages}, **options)

    def pdf_protect(self, source: Any, user_password: str, owner_password: str = "", **options: Any) -> ConversionJob:
        return self.pdf(source, "protect", {
            "userPassword": user_password,
            "ownerPassword": owner_password,
        }, **options)

    def pdf_unlock(self, source: Any, password: str, **options: Any) -> ConversionJob:
        return self.pdf(source, "unlock", {"password": password}, **options)

    def pdf_flatten(self, source: Any, **options: Any) -> ConversionJob:
        return self.pdf(source, "flatten", {}, **options)

    def pdf_resize(self, source: Any, width: int | None = None, height: int | None = None, **options: Any) -> ConversionJob:
        return self.pdf(source, "resize", {"width": width, "height": height}, **options)

    def pdf_crop(self, source: Any, left: int = 0, top: int = 0, width: int | None = None, height: int | None = None, **options: Any) -> ConversionJob:
        return self.pdf(source, "crop", {"left": left, "top": top, "width": width, "height": height}, **options)

    def pdf_organize(self, source: Any, pages: str = "", **options: Any) -> ConversionJob:
        return self.pdf(source, "organize", {"pages": pages}, **options)

    def pdf_extract_images(self, source: Any, **options: Any) -> ConversionJob:
        return self.pdf(source, "extract-images", {}, **options)

    def pdf_remove_pages(self, source: Any, pages: str = "", **options: Any) -> ConversionJob:
        return self.pdf(source, "remove-pages", {"pages": pages}, **options)

    def pdf_extract_pages(self, source: Any, ranges: str = "", **options: Any) -> ConversionJob:
        return self.pdf(source, "extract-pages", {"ranges": ranges}, **options)

    def social_resize(self, source: Any, platform: str, selected_size_ids: list[str], **options: Any) -> ConversionJob:
        upload = self._client.normalize_upload(source, options)
        return self._client.submit_job(
            "/tools/social-resize",
            self._client.filter_none(
                {
                    "fileId": upload.file_id,
                    "inputKey": upload.input_key,
                    "originalName": options.get("original_name", upload.file_name),
                    "platform": platform,
                    "selectedSizeIds": selected_size_ids,
                    "outputFormat": options.get("output_format", "jpg"),
                    "offsets": options.get("offsets", {}),
                    "fileSizeBytes": options.get("file_size_bytes"),
                }
            ),
        )

    def image_resize(self, source: Any, **params: Any) -> ConversionJob:
        return self.image(source, "resize", {
            "width": params.get("width"),
            "height": params.get("height"),
            "fit": params.get("fit", "inside"),
            "outputFormat": params.get("output_format", "jpg"),
        }, **params)

    def image_crop(self, source: Any, left: int, top: int, width: int, height: int, **options: Any) -> ConversionJob:
        return self.image(source, "crop", {
            "left": left,
            "top": top,
            "width": width,
            "height": height,
            "outputFormat": options.get("output_format", "jpg"),
        }, **options)

    def image_rotate(self, source: Any, angle: int = 90, **options: Any) -> ConversionJob:
        return self.image(source, "rotate", {
            "angle": angle,
            "outputFormat": options.get("output_format", "jpg"),
        }, **options)

    def image_flip(self, source: Any, direction: str = "horizontal", **options: Any) -> ConversionJob:
        return self.image(source, "flip", {
            "direction": direction,
            "outputFormat": options.get("output_format", "jpg"),
        }, **options)

    def image_upscale(self, source: Any, scale: float = 2, **options: Any) -> ConversionJob:
        return self.image(source, "upscale", {
            "scale": scale,
            "width": options.get("width"),
            "height": options.get("height"),
            "outputFormat": options.get("output_format", "jpg"),
        }, **options)

    def video_trim(self, source: Any, start_time: float = 0, end_time: float | None = None, **options: Any) -> ConversionJob:
        return self.video(source, "trim", {
            "outputFormat": options.get("output_format", "mp4"),
            "trim": {
                "enabled": True,
                "startTime": start_time,
                "endTime": end_time,
            },
        }, **options)

    def video_extract(self, source: Any, start_time: float = 0, end_time: float | None = None, **options: Any) -> ConversionJob:
        return self.video(source, "extract", {
            "outputFormat": options.get("output_format", "mp4"),
            "trim": {
                "enabled": True,
                "startTime": start_time,
                "endTime": end_time,
            },
        }, **options)

    def video_crop(self, source: Any, left: int, top: int, width: int, height: int, **options: Any) -> ConversionJob:
        return self.video(source, "crop", {
            "left": left,
            "top": top,
            "width": width,
            "height": height,
            "outputFormat": options.get("output_format", "mp4"),
        }, **options)

    def ocr(self, source: Any, target_format: str = "ocr-pdf", **options: Any) -> ConversionJob:
        upload = self._client.normalize_upload(source, options)
        return self._client.submit_job(
            "/tools/ocr",
            {
                "fileId": upload.file_id,
                "inputKey": upload.input_key,
                "targetFormat": target_format,
                "originalName": options.get("original_name", upload.file_name),
                "language": options.get("language", "eng"),
            },
        )

    def pdf(self, source: Any, operation: str, params: dict[str, Any] | None = None, **options: Any) -> ConversionJob:
        payload: dict[str, Any] = {"operation": operation, "params": params or {}}
        if operation == "merge":
            merge_sources = source if isinstance(source, list) else options.get("sources")
            if not isinstance(merge_sources, list) or not merge_sources:
                raise DopplrHubError("PDF merge requires a list of sources.")
            uploads = self._client.normalize_uploads(merge_sources)
            payload["fileId"] = uploads[0].file_id
            payload["inputKeys"] = [item.input_key for item in uploads]
            payload["inputKey"] = payload["inputKeys"][0]
            payload["originalName"] = options.get("original_name", uploads[0].file_name)
        else:
            upload = self._client.normalize_upload(source, options)
            payload["fileId"] = upload.file_id
            payload["inputKey"] = upload.input_key
            payload["originalName"] = options.get("original_name", upload.file_name)

        return self._client.submit_job("/tools/pdf", payload)

    def image(self, source: Any, operation: str, params: dict[str, Any] | None = None, **options: Any) -> ConversionJob:
        upload = self._client.normalize_upload(source, options)
        return self._client.submit_job(
            "/tools/image",
            {
                "operation": operation,
                "fileId": upload.file_id,
                "inputKey": upload.input_key,
                "originalName": options.get("original_name", upload.file_name),
                "params": params or {},
            },
        )

    def video(self, source: Any, operation: str, params: dict[str, Any] | None = None, **options: Any) -> ConversionJob:
        upload = self._client.normalize_upload(source, options)
        return self._client.submit_job(
            "/tools/video",
            {
                "operation": operation,
                "fileId": upload.file_id,
                "inputKey": upload.input_key,
                "originalName": options.get("original_name", upload.file_name),
                "params": params or {},
            },
        )

    def archive(self, sources: list[Any], target_format: str = "zip", **options: Any) -> ConversionJob:
        uploads = self._client.normalize_uploads(sources)
        return self._client.submit_job(
            "/tools/archive",
            {
                "inputKeys": [item.input_key for item in uploads],
                "fileNames": [item.file_name for item in uploads],
                "targetFormat": target_format,
                "archiveName": options.get("archive_name", "archive"),
                "inputPassword": options.get("input_password", ""),
                "outputPassword": options.get("output_password", ""),
            },
        )

    def ada(self, source: Any, **options: Any) -> ImmediateResult:
        upload = self._client.normalize_upload(source, options)
        response = self._client.request_json(
            "POST",
            "/tools/ada/analyze",
            json=self._client.filter_none(
                {
                    "fileId": upload.file_id,
                    "inputKey": upload.input_key,
                    "originalName": options.get("original_name", upload.file_name),
                    "contentType": options.get("content_type"),
                }
            ),
        )
        return ImmediateResult(self._client, response, "reportDownloadUrl", "reportKey")

    def ats(self, source: Any, job_description: str, **options: Any) -> ImmediateResult:
        upload = self._client.normalize_upload(source, options)
        response = self._client.request_json(
            "POST",
            "/tools/ats/analyze",
            json=self._client.filter_none(
                {
                    "fileId": upload.file_id,
                    "inputKey": upload.input_key,
                    "originalName": options.get("original_name", upload.file_name),
                    "contentType": options.get("content_type"),
                    "jobDescription": job_description,
                    "industry": options.get("industry"),
                    "templateId": options.get("template_id"),
                }
            ),
        )
        return ImmediateResult(self._client, response, "optimizedResumeDownloadUrl", "optimizedResumeKey")

    def ats_reexport(self, report: dict[str, Any], template_id: str, **options: Any) -> ImmediateResult:
        response = self._client.request_json(
            "POST",
            "/tools/ats/reexport",
            json=self._client.filter_none(
                {
                    "report": report,
                    "templateId": template_id,
                    "fileId": options.get("file_id"),
                    "originalName": options.get("original_name"),
                }
            ),
        )
        return ImmediateResult(
            self._client,
            response,
            "optimizedResumeDownloadUrl",
            None,
            options.get("download_as", "optimized-resume.docx"),
        )


class DopplrHub:
    def __init__(self, api_key: str, base_url: str = "https://api.dopplrhub.com/api/v1", timeout_seconds: int = 120) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()
        self.tools = ToolsClient(self)
        self.utilities = UtilitiesClient(self)

    def upload(self, file_path: str | Path) -> UploadedFile:
        path = Path(file_path).expanduser().resolve()
        if not path.is_file():
            raise DopplrHubError(f"Input file not found: {file_path}")

        with path.open("rb") as handle:
            response = self.request_json(
                "POST",
                "/upload",
                files={"file": (path.name, handle, "application/octet-stream")},
            )
        return UploadedFile(response)

    def import_from_url(self, url: str, **options: Any) -> UploadedFile:
        file_name = options.get("file_name") or self.detect_remote_file_name(url)
        payload = {"url": url, "fileName": file_name}
        if "content_type" in options:
            payload["contentType"] = options["content_type"]
        if "auth_header" in options:
            payload["authHeader"] = options["auth_header"]
        return UploadedFile(self.request_json("POST", "/upload/from-url", json=payload))

    def start(self, file_path: str | Path, target_format: str, **options: Any) -> ConversionJob:
        return self.convert(self.upload(file_path), target_format, **options)

    def start_from_contents(self, contents: bytes | str, file_name: str, target_format: str) -> ConversionJob:
        from tempfile import NamedTemporaryFile

        data = contents.encode("utf-8") if isinstance(contents, str) else contents
        suffix = Path(file_name).suffix
        with NamedTemporaryFile(delete=False, suffix=suffix or ".bin") as handle:
            handle.write(data)
            temp_path = Path(handle.name)

        try:
            upload = self.upload(temp_path)
            return self.convert(upload, target_format, original_name=file_name)
        finally:
            temp_path.unlink(missing_ok=True)

    def start_from_url(self, url: str, target_format: str, **options: Any) -> ConversionJob:
        upload = self.import_from_url(url, **options)
        return self.convert(
            upload,
            target_format,
            original_name=options.get("original_name") or options.get("file_name"),
            media_type=options.get("media_type"),
            conversion_settings=options.get("conversion_settings"),
        )

    def convert(self, source: Any, target_format: str, **options: Any) -> ConversionJob:
        upload = self.normalize_upload(source, options)
        return self.submit_job(
            "/convert",
            {
                "fileId": upload.file_id,
                "inputKey": upload.input_key,
                "targetFormat": target_format,
                "originalName": options.get("original_name", upload.file_name),
                "mediaType": options.get("media_type"),
                "conversionSettings": options.get("conversion_settings"),
            },
        )

    def get_job(self, job_id: str) -> dict[str, Any]:
        return self.request_json("GET", f"/jobs/{quote(job_id)}")

    def delete_job(self, job_id: str) -> None:
        self.request_json("DELETE", f"/jobs/{quote(job_id)}")

    def download_file(self, url: str, target_path: str | Path) -> Path:
        output = Path(target_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        response = requests.get(url, stream=True, timeout=max(self.timeout_seconds, 60))
        if response.status_code >= 400:
            raise DopplrHubError(f"Download failed with HTTP {response.status_code}.")
        with output.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=65536):
                if chunk:
                    handle.write(chunk)
        return output

    def extension_from_payload(self, payload: dict[str, Any]) -> str:
        output_key = str(payload.get("outputKey") or payload.get("reportKey") or payload.get("optimizedResumeKey") or "")
        if output_key:
            suffix = Path(output_key).suffix.lstrip(".")
            if suffix:
                return suffix.lower()
        return self.guess_extension(str(payload.get("targetFormat") or "bin"))

    @staticmethod
    def guess_extension(target_format: str) -> str:
        normalized = target_format.strip().lower()
        parts = normalized.split("-")
        return parts[-1] if parts else normalized

    def normalize_upload(self, source: Any, options: dict[str, Any] | None = None) -> UploadedFile:
        if isinstance(source, UploadedFile):
            return source
        if isinstance(source, dict) and "fileId" in source and "inputKey" in source:
            return UploadedFile(source)
        if isinstance(source, (str, Path)):
            source_text = str(source)
            if source_text.lower().startswith(("http://", "https://")):
                return self.import_from_url(source_text, **(options or {}))
            return self.upload(source_text)
        raise DopplrHubError("Source must be a local file path, remote URL, UploadedFile, or upload response dict.")

    def normalize_uploads(self, sources: list[Any]) -> list[UploadedFile]:
        if not sources:
            raise DopplrHubError("At least one source is required.")
        return [self.normalize_upload(source) for source in sources]

    def submit_job(self, endpoint: str, payload: dict[str, Any]) -> ConversionJob:
        filtered = self.filter_none(payload)
        response = self.request_json("POST", endpoint, json=filtered)
        if "originalName" not in response and "originalName" in filtered:
            response["originalName"] = filtered["originalName"]
        return ConversionJob(self, response)

    def request_json(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        response = self.request(method, path, **kwargs)
        self.raise_for_error(response)
        try:
            data = response.json()
        except ValueError as exc:
            raise DopplrHubError(
                f"Expected JSON response for {method} {path}, got: {response.text.strip() or '[empty body]'}"
            ) from exc
        if not isinstance(data, dict):
            raise DopplrHubError(f"Expected JSON object for {method} {path}.")
        return data

    def request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        url = path if kwargs.pop("absolute_url", False) else f"{self.base_url}/{path.lstrip('/')}"
        headers = {"x-api-key": self.api_key, **kwargs.pop("headers", {})}
        return self.session.request(method, url, headers=headers, timeout=self.timeout_seconds, **kwargs)

    @staticmethod
    def filter_none(payload: dict[str, Any]) -> dict[str, Any]:
        return {key: value for key, value in payload.items() if value is not None}

    @staticmethod
    def raise_for_error(response: requests.Response) -> None:
        if response.status_code < 400:
            return
        try:
            body = response.json()
        except ValueError:
            body = None
        message = body.get("error") if isinstance(body, dict) else None
        raise DopplrHubError(str(message or f"HTTP {response.status_code}"))

    @staticmethod
    def detect_remote_file_name(url: str) -> str:
        name = Path(urlparse(url).path).name
        return name or "remote-input.bin"
