from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings
from app.modules.trading_import.model import TradingImportDocumentType


@dataclass(frozen=True)
class StoredUpload:
    original_filename: str
    stored_filename: str
    storage_path: str
    content_type: str | None
    file_size: int


class TradingImportStorage:
    def __init__(self) -> None:
        configured_path = Path(settings.trading_import_data_dir)
        self.base_path = configured_path if configured_path.is_absolute() else Path.cwd() / configured_path
        self.max_bytes = settings.trading_import_max_upload_mb * 1024 * 1024

    async def save_pdf(
        self,
        *,
        record_id: int,
        document_type: TradingImportDocumentType,
        file: UploadFile,
    ) -> StoredUpload:
        original_filename = Path(file.filename or "").name
        if not original_filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are supported")

        stored_filename = f"{uuid4().hex}.pdf"
        relative_dir = Path("records") / str(record_id) / document_type.value
        absolute_dir = self.base_path / relative_dir
        absolute_dir.mkdir(parents=True, exist_ok=True)
        absolute_path = absolute_dir / stored_filename

        file_size = 0
        try:
            with absolute_path.open("wb") as destination:
                while chunk := await file.read(1024 * 1024):
                    file_size += len(chunk)
                    if file_size > self.max_bytes:
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f"PDF exceeds {settings.trading_import_max_upload_mb} MB upload limit",
                        )
                    destination.write(chunk)
        except Exception:
            absolute_path.unlink(missing_ok=True)
            raise
        finally:
            await file.close()

        return StoredUpload(
            original_filename=original_filename,
            stored_filename=stored_filename,
            storage_path=(relative_dir / stored_filename).as_posix(),
            content_type=file.content_type,
            file_size=file_size,
        )

    def resolve_path(self, storage_path: str) -> Path:
        resolved = (self.base_path / storage_path).resolve()
        base = self.base_path.resolve()
        if base != resolved and base not in resolved.parents:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document path")
        return resolved

    def delete(self, storage_path: str | None) -> None:
        if not storage_path:
            return
        self.resolve_path(storage_path).unlink(missing_ok=True)
