from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.common.response import make_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_module_access
from app.modules.trading_import.model import TradingImportDocumentType
from app.modules.trading_import.schemas import (
    TradingImportRecordCreate,
    TradingImportRecordRead,
    TradingImportRecordUpdate,
    TradingSalesDetentionInvoiceRead,
    TradingSalesDetentionInvoiceUpsert,
    TradingSalesDocumentRead,
    TradingSalesFormRead,
    TradingSalesFormUpsert,
    TradingSalesFreightInvoiceRead,
    TradingSalesFreightInvoiceUpsert,
    TradingSalesPaymentReceiptCreate,
    TradingSalesPaymentReceiptRead,
)
from app.modules.trading_import.service import TradingImportService
from app.modules.users.model import User


router = APIRouter(prefix="/trading-import/sales", tags=["Trading Import Sales"])
require_trading_import_sales = require_module_access("sales")


@router.get("/records")
def list_records(
    db: Session = Depends(get_db),
    _: User = Depends(require_trading_import_sales),
):
    records = TradingImportService(db).list_records()
    return make_response(
        True,
        "Trading import records fetched successfully",
        [_serialize_record(record) for record in records],
    )


@router.post("/records")
def create_record(
    payload: TradingImportRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_trading_import_sales),
):
    record = TradingImportService(db).create_record(
        reference_no=payload.reference_no,
        title=payload.title,
        customer=payload.customer,
        salesperson=payload.salesperson,
        company=payload.company,
        expected_arrival_date=payload.expected_arrival_date,
        remarks=payload.remarks,
        actor=current_user,
    )
    return make_response(True, "Trading import record created successfully", _serialize_record(record))


@router.get("/records/{record_id}")
def get_record(
    record_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_trading_import_sales),
):
    record = TradingImportService(db).get_record(record_id)
    return make_response(True, "Trading import record fetched successfully", _serialize_record(record))


@router.patch("/records/{record_id}")
def update_record(
    record_id: int,
    payload: TradingImportRecordUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_trading_import_sales),
):
    record = TradingImportService(db).update_record(
        record_id=record_id,
        reference_no=payload.reference_no,
        title=payload.title,
        customer=payload.customer,
        salesperson=payload.salesperson,
        company=payload.company,
        expected_arrival_date=payload.expected_arrival_date,
        remarks=payload.remarks,
        status_value=payload.status,
    )
    return make_response(True, "Trading import record updated successfully", _serialize_record(record))


@router.post("/records/{record_id}/documents/{document_type}/upload")
async def upload_document(
    record_id: int,
    document_type: TradingImportDocumentType,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_trading_import_sales),
):
    document = await TradingImportService(db).upload_document(
        record_id=record_id,
        document_type=document_type,
        file=file,
        actor=current_user,
    )
    return make_response(True, "Document uploaded successfully", _serialize_document(document))


@router.get("/records/{record_id}/documents/{document_type}/download")
def download_document(
    record_id: int,
    document_type: TradingImportDocumentType,
    db: Session = Depends(get_db),
    _: User = Depends(require_trading_import_sales),
):
    document, path = TradingImportService(db).resolve_document_path(
        record_id=record_id,
        document_type=document_type,
    )
    return FileResponse(path=path, filename=document.original_filename, media_type="application/pdf")


@router.put("/records/{record_id}/forms/{document_type}")
def upsert_form(
    record_id: int,
    document_type: TradingImportDocumentType,
    payload: TradingSalesFormUpsert,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_trading_import_sales),
):
    form = TradingImportService(db).upsert_form(
        record_id=record_id,
        document_type=document_type,
        data=payload.data,
        completed=payload.completed,
        actor=current_user,
    )
    return make_response(True, "Document form saved successfully", _serialize_form(form))


@router.get("/records/{record_id}/suggestions")
def get_suggestions(
    record_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_trading_import_sales),
):
    suggestions = TradingImportService(db).get_suggestions(record_id)
    return make_response(True, "Suggestions fetched successfully", suggestions)


@router.get("/records/{record_id}/freight-invoice/render")
def get_freight_invoice_render(
    record_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_trading_import_sales),
):
    render_data = TradingImportService(db).get_freight_invoice_render(record_id)
    return make_response(True, "Freight invoice render data fetched successfully", render_data)


@router.put("/records/{record_id}/freight-invoice")
def upsert_freight_invoice(
    record_id: int,
    payload: TradingSalesFreightInvoiceUpsert,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_trading_import_sales),
):
    invoice = TradingImportService(db).upsert_freight_invoice(
        record_id=record_id,
        payload=payload,
        actor=current_user,
    )
    return make_response(True, "Freight invoice saved successfully", _serialize_freight_invoice(invoice))


@router.post("/records/{record_id}/payment-receipts")
def create_payment_receipt(
    record_id: int,
    payload: TradingSalesPaymentReceiptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_trading_import_sales),
):
    receipt = TradingImportService(db).create_payment_receipt(
        record_id=record_id,
        payload=payload,
        actor=current_user,
    )
    return make_response(True, "Payment receipt created successfully", _serialize_payment_receipt(receipt))


@router.get("/records/{record_id}/payment-receipts")
def list_payment_receipts(
    record_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_trading_import_sales),
):
    record = TradingImportService(db).get_record(record_id)
    return make_response(
        True,
        "Payment receipts fetched successfully",
        [_serialize_payment_receipt(receipt) for receipt in record.payment_receipts],
    )


@router.put("/records/{record_id}/detention-invoice")
def upsert_detention_invoice(
    record_id: int,
    payload: TradingSalesDetentionInvoiceUpsert,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_trading_import_sales),
):
    invoice = TradingImportService(db).upsert_detention_invoice(
        record_id=record_id,
        payload=payload,
        actor=current_user,
    )
    return make_response(True, "Detention invoice saved successfully", _serialize_detention_invoice(invoice))


def _serialize_record(record) -> dict:
    return TradingImportRecordRead.model_validate(record).model_dump(mode="json")


def _serialize_document(document) -> dict:
    return TradingSalesDocumentRead.model_validate(document).model_dump(mode="json")


def _serialize_form(form) -> dict:
    return TradingSalesFormRead.model_validate(form).model_dump(mode="json")


def _serialize_freight_invoice(invoice) -> dict:
    return TradingSalesFreightInvoiceRead.model_validate(invoice).model_dump(mode="json")


def _serialize_payment_receipt(receipt) -> dict:
    return TradingSalesPaymentReceiptRead.model_validate(receipt).model_dump(mode="json")


def _serialize_detention_invoice(invoice) -> dict:
    return TradingSalesDetentionInvoiceRead.model_validate(invoice).model_dump(mode="json")
