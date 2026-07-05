from datetime import date, datetime
from decimal import Decimal
from typing import Any

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.modules.trading_import.model import (
    TradingImportDocumentType,
    TradingImportRecordStatus,
    TradingSalesDetentionInvoice,
    TradingSalesDocument,
    TradingSalesForm,
    TradingSalesFreightInvoice,
    TradingSalesImportRecord,
    TradingSalesPaymentReceipt,
)
from app.modules.trading_import.repository import TradingImportRepository
from app.modules.trading_import.schemas import (
    TradingSalesDetentionInvoiceUpsert,
    TradingSalesFreightInvoiceUpsert,
    TradingSalesPaymentReceiptCreate,
)
from app.modules.trading_import.storage import TradingImportStorage
from app.modules.users.model import User


CANONICAL_FIELD_ALIASES: dict[str, list[str]] = {
    "bill_to": ["bill to", "billto", "invoice bill to", "customer"],
    "ntn_no": ["ntn no", "ntn", "tax no", "tax number", "ntnNo"],
    "clearing_agent": ["clearing agent", "clearing agent name", "cha", "custom agent", "clearingAgent"],
    "shipper": ["shipper", "exporter", "consignor"],
    "consignee": ["consignee", "importer"],
    "notify_party": ["notify party", "notify", "notifyParty"],
    "forwarding_agent": ["forwarding agent", "agent", "forwardingAgent"],
    "booking_no": ["booking no", "booking number", "booking", "bookingNo", "bookingNumber"],
    "draft_bl_no": ["draft bl no", "draft bill no", "draftBlNo"],
    "hbl_no": ["hbl no", "house bl no", "house bill no", "bill of lading no", "hblNumber"],
    "mbl_no": ["mbl no", "master bl no", "master bill no", "bl no", "mblNumber"],
    "vessel": ["vessel", "vessel name"],
    "voyage_no": ["voyage", "voyage no", "voy no", "voyageNo"],
    "place_of_receipt": ["place of receipt", "placeOfReceipt"],
    "pol": ["pol", "port of loading", "load port"],
    "pod": ["pod", "port of discharge", "discharge port"],
    "place_of_delivery": ["place of delivery", "final destination", "placeOfDelivery"],
    "eta": ["eta", "estimated arrival"],
    "marks_no": ["marks", "marks no", "marks and no", "marksAndNumbers"],
    "container_no": ["container no", "container number", "container", "containerNo"],
    "container_summary": ["container summary", "container size", "container count", "container type", "containerSummary", "containerType"],
    "seal_no": ["seal no", "seal number", "seal", "sealNo"],
    "packages": ["packages", "no of packages", "quantity"],
    "goods_description": ["description", "goods description", "description of goods", "commodity", "cargoDescription"],
    "hs_code": ["hs code", "hscode", "hsCode"],
    "gross_weight": ["gross weight", "gr wt", "gross wt", "grossWeight"],
    "net_weight": ["net weight", "net wt", "netWeight"],
    "measurement": ["measurement", "m3", "cbm"],
    "free_days": ["free days", "detention free days", "free detention", "freeDays"],
    "shipping_line": ["shipping line", "carrier", "ocean carrier", "shippingLine"],
    "destination": ["destination", "final destination"],
    "freight_terms": ["freight", "freight terms", "freight prepaid", "freightTerms"],
}
DOCUMENT_PRECEDENCE = (
    TradingImportDocumentType.HOUSE_BL,
    TradingImportDocumentType.MASTER_BL,
    TradingImportDocumentType.DRAFT_BL,
)

INVOICE_AUTO_FIELD_KEYS = (
    "bill_to",
    "ntn_no",
    "clearing_agent",
    "container_summary",
    "container_no",
    "vessel",
    "voyage_no",
    "shipping_line",
    "shipper",
    "consignee",
    "goods_description",
    "hs_code",
    "hbl_no",
    "mbl_no",
    "gross_weight",
    "net_weight",
    "pol",
    "pod",
    "destination",
)

INVOICE_MANUAL_FIELD_KEYS = (
    "al_bashar_chal",
    "invoice_no",
    "invoice_date",
    "exchange_rate",
)

MANUAL_CHARGE_CODES = (
    "THC",
    "EMF",
    "ISPS",
    "GATE_PASS",
    "ISC",
    "CAFD",
    "LOLO",
    "DOCUMENTATION",
    "LATE_DO",
    "BL_AMENDMENT",
    "SECURITY_DEPOSIT_LOCAL_KARACHI",
    "SECURITY_DEPOSIT_UPCOUNTRY",
    "DETENTION_ADVANCE_RENT_PER_DAY",
)


class TradingImportService:
    def __init__(self, db: Session):
        self.repository = TradingImportRepository(db)
        self.storage = TradingImportStorage()

    def list_records(self) -> list[TradingSalesImportRecord]:
        return self.repository.list_records()

    def get_record(self, record_id: int) -> TradingSalesImportRecord:
        return self._get_record_or_404(record_id)

    def create_record(
        self,
        *,
        reference_no: str | None,
        title: str | None,
        actor: User,
    ) -> TradingSalesImportRecord:
        if reference_no and self.repository.get_by_reference_no(reference_no):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Reference number already exists")

        return self.repository.create_record(
            reference_no=reference_no,
            title=title,
            status=TradingImportRecordStatus.DRAFT,
            created_by=actor.id,
        )

    def update_record(
        self,
        *,
        record_id: int,
        reference_no: str | None,
        title: str | None,
        status_value: TradingImportRecordStatus | None,
    ) -> TradingSalesImportRecord:
        record = self._get_record_or_404(record_id)
        if reference_no is not None:
            existing = self.repository.get_by_reference_no(reference_no)
            if existing and existing.id != record.id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Reference number already exists")

        return self.repository.update_record(
            record,
            reference_no=reference_no,
            title=title,
            status=status_value,
        )

    async def upload_document(
        self,
        *,
        record_id: int,
        document_type: TradingImportDocumentType,
        file: UploadFile,
        actor: User,
    ) -> TradingSalesDocument:
        self._get_record_or_404(record_id)
        previous_document = self.repository.get_document(record_id=record_id, document_type=document_type)
        previous_path = previous_document.storage_path if previous_document else None

        stored_upload = await self.storage.save_pdf(record_id=record_id, document_type=document_type, file=file)
        document = self.repository.upsert_document(
            record_id=record_id,
            document_type=document_type,
            values={
                "original_filename": stored_upload.original_filename,
                "stored_filename": stored_upload.stored_filename,
                "storage_path": stored_upload.storage_path,
                "content_type": stored_upload.content_type,
                "file_size": stored_upload.file_size,
                "uploaded_by": actor.id,
                "uploaded_at": datetime.utcnow(),
            },
        )
        self.storage.delete(previous_path)
        self._refresh_record_status(record_id)
        return document

    def resolve_document_path(
        self,
        *,
        record_id: int,
        document_type: TradingImportDocumentType,
    ):
        self._get_record_or_404(record_id)
        document = self.repository.get_document(record_id=record_id, document_type=document_type)
        if document is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not uploaded")

        path = self.storage.resolve_path(document.storage_path)
        if not path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Uploaded document file is missing")

        return document, path

    def upsert_form(
        self,
        *,
        record_id: int,
        document_type: TradingImportDocumentType,
        data: dict[str, Any],
        completed: bool,
        actor: User,
    ) -> TradingSalesForm:
        self._get_record_or_404(record_id)
        form = self.repository.upsert_form(
            record_id=record_id,
            document_type=document_type,
            values={
                "data": data,
                "canonical_data": _extract_canonical_data(data),
                "completed_by": actor.id if completed else None,
                "completed_at": datetime.utcnow() if completed else None,
            },
        )
        self._refresh_record_status(record_id)
        return form

    def get_suggestions(self, record_id: int) -> dict[str, Any]:
        record = self._get_record_or_404(record_id)
        by_field: dict[str, list[Any]] = {}
        all_values: list[Any] = []

        for form in record.forms:
            flattened = _flatten_mapping(form.data)
            for field_name, value in flattened.items():
                if not _is_suggestion_value(value):
                    continue
                label = field_name.replace(".", " ").replace("_", " ").strip()
                by_field.setdefault(label, [])
                if value not in by_field[label]:
                    by_field[label].append(value)
                if value not in all_values:
                    all_values.append(value)

        return {"by_field": by_field, "all": all_values}

    def get_freight_invoice_render(self, record_id: int) -> dict[str, Any]:
        record = self._get_record_or_404(record_id)
        charges = record.freight_invoice.charges if record.freight_invoice else []
        manual_fields = record.freight_invoice.manual_fields if record.freight_invoice else {}
        invoice_no = record.freight_invoice.invoice_no if record.freight_invoice else None
        return self._build_freight_invoice_render(record, invoice_no, charges, manual_fields)

    def upsert_freight_invoice(
        self,
        *,
        record_id: int,
        payload: TradingSalesFreightInvoiceUpsert,
        actor: User,
    ) -> TradingSalesFreightInvoice:
        record = self._get_record_or_404(record_id)
        charges = [_json_safe(item.model_dump()) for item in payload.charges]
        render_data = self._build_freight_invoice_render(record, payload.invoice_no, charges, payload.manual_fields)
        invoice = self.repository.upsert_freight_invoice(
            record_id=record_id,
            values={
                "invoice_no": payload.invoice_no,
                "charges": charges,
                "manual_fields": payload.manual_fields,
                "render_data": render_data,
                "created_by": actor.id,
            },
        )
        self.repository.update_record(record, status=TradingImportRecordStatus.INVOICED)
        return invoice

    def create_payment_receipt(
        self,
        *,
        record_id: int,
        payload: TradingSalesPaymentReceiptCreate,
        actor: User,
    ) -> TradingSalesPaymentReceipt:
        record = self._get_record_or_404(record_id)
        if record.freight_invoice is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Create the freight invoice before recording a payment",
            )

        render_data = self._build_payment_receipt_render(record, payload)
        receipt = self.repository.create_payment_receipt(
            record_id=record_id,
            receipt_no=payload.receipt_no,
            tid=payload.tid,
            amount=payload.amount,
            currency=payload.currency,
            payment_date=payload.payment_date,
            render_data=render_data,
            created_by=actor.id,
        )
        self.repository.update_record(record, status=TradingImportRecordStatus.PAID)
        return receipt

    def upsert_detention_invoice(
        self,
        *,
        record_id: int,
        payload: TradingSalesDetentionInvoiceUpsert,
        actor: User,
    ) -> TradingSalesDetentionInvoice:
        record = self._get_record_or_404(record_id)
        if payload.detention_end < payload.detention_start:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Detention end date cannot be before start date",
            )

        total_days = (payload.detention_end - payload.detention_start).days + 1
        chargeable_days = max(total_days - payload.free_days, 0)
        detention_amount = payload.per_day_amount * Decimal(chargeable_days)
        refund_amount = payload.security_deposit - detention_amount
        render_data = self._build_detention_invoice_render(
            record=record,
            payload=payload,
            chargeable_days=chargeable_days,
            detention_amount=detention_amount,
            refund_amount=refund_amount,
        )

        invoice = self.repository.upsert_detention_invoice(
            record_id=record_id,
            values={
                "invoice_no": payload.invoice_no,
                "detention_start": payload.detention_start,
                "detention_end": payload.detention_end,
                "free_days": payload.free_days,
                "chargeable_days": chargeable_days,
                "per_day_amount": payload.per_day_amount,
                "detention_amount": detention_amount,
                "security_deposit": payload.security_deposit,
                "refund_amount": refund_amount,
                "currency": payload.currency,
                "manual_fields": payload.manual_fields,
                "render_data": render_data,
                "created_by": actor.id,
            },
        )
        self.repository.update_record(record, status=TradingImportRecordStatus.DETENTION)
        return invoice

    def _build_freight_invoice_render(
        self,
        record: TradingSalesImportRecord,
        invoice_no: str | None,
        charges: list[dict[str, Any]],
        manual_fields: dict[str, Any],
    ) -> dict[str, Any]:
        context = _merge_canonical_context(record)
        total_amount = sum(Decimal(str(charge.get("amount", 0))) for charge in charges)
        currency = charges[0].get("currency", "PKR") if charges else manual_fields.get("currency", "PKR")
        auto_fields = _pick_fields(context, INVOICE_AUTO_FIELD_KEYS)
        manual_header_fields = _pick_fields(manual_fields, INVOICE_MANUAL_FIELD_KEYS)
        return _json_safe(
            {
                "document_type": "freight_invoice",
                "record_id": record.id,
                "reference_no": record.reference_no,
                "invoice_no": invoice_no,
                "currency": currency,
                "total_amount": total_amount,
                "header": context,
                "auto_fields": auto_fields,
                "manual_entry": {
                    "header_fields": manual_header_fields,
                    "required_header_fields": list(INVOICE_MANUAL_FIELD_KEYS),
                    "charge_codes": list(MANUAL_CHARGE_CODES),
                    "charges": charges,
                },
                "charges": charges,
                "manual_fields": manual_fields,
            }
        )

    def _build_payment_receipt_render(
        self,
        record: TradingSalesImportRecord,
        payload: TradingSalesPaymentReceiptCreate,
    ) -> dict[str, Any]:
        invoice_render = record.freight_invoice.render_data if record.freight_invoice else {}
        return _json_safe(
            {
                "document_type": "import_payment_receipt",
                "record_id": record.id,
                "reference_no": record.reference_no,
                "receipt_no": payload.receipt_no,
                "tid": payload.tid,
                "amount": payload.amount,
                "currency": payload.currency,
                "payment_date": payload.payment_date,
                "invoice": invoice_render,
            }
        )

    def _build_detention_invoice_render(
        self,
        *,
        record: TradingSalesImportRecord,
        payload: TradingSalesDetentionInvoiceUpsert,
        chargeable_days: int,
        detention_amount: Decimal,
        refund_amount: Decimal,
    ) -> dict[str, Any]:
        context = _merge_canonical_context(record)
        auto_fields = _pick_fields(context, INVOICE_AUTO_FIELD_KEYS)
        return _json_safe(
            {
                "document_type": "detention_invoice",
                "record_id": record.id,
                "reference_no": record.reference_no,
                "invoice_no": payload.invoice_no,
                "header": context,
                "auto_fields": auto_fields,
                "manual_entry": {
                    "header_fields": _pick_fields(payload.manual_fields, INVOICE_MANUAL_FIELD_KEYS),
                    "required_header_fields": list(INVOICE_MANUAL_FIELD_KEYS),
                    "date_and_charge_fields": [
                        "detention_start",
                        "detention_end",
                        "free_days",
                        "per_day_amount",
                        "security_deposit",
                    ],
                },
                "detention": {
                    "detention_start": payload.detention_start,
                    "detention_end": payload.detention_end,
                    "free_days": payload.free_days,
                    "chargeable_days": chargeable_days,
                    "per_day_amount": payload.per_day_amount,
                    "detention_amount": detention_amount,
                    "security_deposit": payload.security_deposit,
                    "refund_amount": refund_amount,
                    "currency": payload.currency,
                },
                "manual_fields": payload.manual_fields,
            }
        )

    def _refresh_record_status(self, record_id: int) -> None:
        record = self._get_record_or_404(record_id)
        if record.freight_invoice:
            return

        status_value = TradingImportRecordStatus.IN_PROGRESS
        completed_types = {form.document_type for form in record.forms if form.completed_at is not None}
        if all(document_type in completed_types for document_type in TradingImportDocumentType):
            status_value = TradingImportRecordStatus.READY_FOR_INVOICE
        elif not record.documents and not record.forms:
            status_value = TradingImportRecordStatus.DRAFT

        self.repository.update_record(record, status=status_value)

    def _get_record_or_404(self, record_id: int) -> TradingSalesImportRecord:
        record = self.repository.get_record(record_id)
        if record is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trading import record not found")
        return record


def _extract_canonical_data(data: dict[str, Any]) -> dict[str, Any]:
    flattened = _flatten_mapping(data)
    normalized_lookup = {_normalize_key(key): value for key, value in flattened.items()}
    canonical: dict[str, Any] = {}

    for canonical_key, aliases in CANONICAL_FIELD_ALIASES.items():
        for alias in aliases:
            value = normalized_lookup.get(_normalize_key(alias))
            if value not in (None, ""):
                canonical[canonical_key] = value
                break

    return canonical


def _merge_canonical_context(record: TradingSalesImportRecord) -> dict[str, Any]:
    forms_by_type = {form.document_type: form for form in record.forms}
    context: dict[str, Any] = {}
    for document_type in reversed(DOCUMENT_PRECEDENCE):
        form = forms_by_type.get(document_type)
        if form:
            context.update(form.canonical_data or {})
    return context


def _flatten_mapping(data: Any, prefix: str = "") -> dict[str, Any]:
    if not isinstance(data, dict):
        return {}

    flattened: dict[str, Any] = {}
    for key, value in data.items():
        field_name = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, dict):
            flattened.update(_flatten_mapping(value, field_name))
        elif isinstance(value, list):
            for index, item in enumerate(value):
                if isinstance(item, dict):
                    flattened.update(_flatten_mapping(item, f"{field_name}.{index}"))
                else:
                    flattened[f"{field_name}.{index}"] = item
        else:
            flattened[field_name] = value
    return flattened


def _pick_fields(source: dict[str, Any], field_names: tuple[str, ...]) -> dict[str, Any]:
    return {field_name: source[field_name] for field_name in field_names if source.get(field_name) not in (None, "")}


def _normalize_key(value: str) -> str:
    return "".join(character for character in value.lower() if character.isalnum())


def _is_suggestion_value(value: Any) -> bool:
    return isinstance(value, (str, int, float)) and value not in ("", None)


def _json_safe(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    return value
