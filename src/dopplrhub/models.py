from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class UploadedFile:
    payload: dict[str, Any]

    @property
    def file_id(self) -> str:
        return str(self.payload.get("fileId", ""))

    @property
    def input_key(self) -> str:
        return str(self.payload.get("inputKey", ""))

    @property
    def file_name(self) -> str:
        return str(self.payload.get("fileName", "input.bin"))

    @property
    def file_size(self) -> int | None:
        value = self.payload.get("fileSize")
        return int(value) if value is not None else None

    def to_dict(self) -> dict[str, Any]:
        return dict(self.payload)


class _BaseResult:
    def __init__(self, client: Any, payload: dict[str, Any]) -> None:
        self._client = client
        self._payload = payload

    def to_dict(self) -> dict[str, Any]:
        return dict(self._payload)


class ConversionJob(_BaseResult):
    @property
    def job_id(self) -> str:
        return str(self._payload.get("jobId", ""))

    @property
    def state(self) -> str:
        return str(self._payload.get("state") or self._payload.get("status") or "queued")

    def refresh(self) -> "ConversionJob":
        current = self._client.get_job(self.job_id)
        self._payload.update(current)
        return self

    def wait(self, timeout_seconds: int = 900, poll_seconds: int = 2) -> "ConversionJob":
        import time
        from .exceptions import DopplrHubError

        deadline = time.time() + max(timeout_seconds, 1)
        while time.time() <= deadline:
            self.refresh()
            state = self.state.lower()
            if state == "completed":
                return self
            if state == "failed":
                raise DopplrHubError(str(self._payload.get("failedReason") or "Conversion failed."))
            time.sleep(max(poll_seconds, 1))

        raise DopplrHubError(f"Timed out waiting for conversion job {self.job_id}")

    def download(self, target_path: str | Path | None = None) -> "ConversionJob":
        if self.state.lower() != "completed":
            self.refresh()
        if self.state.lower() != "completed":
            from .exceptions import DopplrHubError
            raise DopplrHubError(f"Job {self.job_id} is not completed.")

        download_url = str(self._payload.get("downloadUrl") or "")
        if not download_url:
            from .exceptions import DopplrHubError
            raise DopplrHubError("Completed job did not include a downloadUrl.")

        output = Path(target_path) if target_path is not None else self._default_download_path()
        self._client.download_file(download_url, output)
        return self

    def delete(self) -> "ConversionJob":
        self._client.delete_job(self.job_id)
        return self

    def _default_download_path(self) -> Path:
        output_key = str(self._payload.get("outputKey") or "")
        if output_key:
            return Path(".") / Path(output_key).name

        original_name = str(self._payload.get("originalName") or "output")
        base_name = Path(original_name).stem or "output"
        extension = self._client.extension_from_payload(self._payload)
        return Path(".") / f"{base_name}.{extension}"


class ImmediateResult(_BaseResult):
    def __init__(
        self,
        client: Any,
        payload: dict[str, Any],
        download_url_field: str,
        download_key_field: str | None = None,
        default_file_name: str | None = None,
    ) -> None:
        super().__init__(client, payload)
        self._download_url_field = download_url_field
        self._download_key_field = download_key_field
        self._default_file_name = default_file_name

    def download(self, target_path: str | Path | None = None) -> "ImmediateResult":
        from .exceptions import DopplrHubError

        download_url = str(self._payload.get(self._download_url_field) or "")
        if not download_url:
            raise DopplrHubError("Response did not include a download URL.")

        output = Path(target_path) if target_path is not None else self._default_download_path()
        self._client.download_file(download_url, output)
        return self

    def _default_download_path(self) -> Path:
        if self._download_key_field:
            download_key = str(self._payload.get(self._download_key_field) or "")
            if download_key:
                return Path(".") / Path(download_key).name

        if self._default_file_name:
            return Path(".") / self._default_file_name

        original_name = str(self._payload.get("originalName") or "download")
        return Path(".") / f"{Path(original_name).stem or 'download'}.bin"
