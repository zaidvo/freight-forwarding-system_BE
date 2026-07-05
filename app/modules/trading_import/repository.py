from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.trading_import.model import (
    TradingImportDocumentType,
    TradingSalesDetentionInvoice,
    TradingSalesDocument,
    TradingSalesForm,
    TradingSalesFreightInvoice,
    TradingSalesImportRecord,
    TradingSalesPaymentReceipt,
)


class TradingImportRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_records(self) -> list[TradingSalesImportRecord]:
        statement = (
            select(TradingSalesImportRecord)
            .options(
                selectinload(TradingSalesImportRecord.documents),
                selectinload(TradingSalesImportRecord.forms),
                selectinload(TradingSalesImportRecord.freight_invoice),
                selectinload(TradingSalesImportRecord.payment_receipts),
                selectinload(TradingSalesImportRecord.detention_invoice),
            )
            .order_by(TradingSalesImportRecord.created_at.desc(), TradingSalesImportRecord.id.desc())
        )
        return list(self.db.scalars(statement).all())

    def get_record(self, record_id: int) -> TradingSalesImportRecord | None:
        statement = (
            select(TradingSalesImportRecord)
            .where(TradingSalesImportRecord.id == record_id)
            .options(
                selectinload(TradingSalesImportRecord.documents),
                selectinload(TradingSalesImportRecord.forms),
                selectinload(TradingSalesImportRecord.freight_invoice),
                selectinload(TradingSalesImportRecord.payment_receipts),
                selectinload(TradingSalesImportRecord.detention_invoice),
            )
        )
        return self.db.scalar(statement)

    def get_by_reference_no(self, reference_no: str) -> TradingSalesImportRecord | None:
        statement = select(TradingSalesImportRecord).where(TradingSalesImportRecord.reference_no == reference_no)
        return self.db.scalar(statement)

    def create_record(self, **values) -> TradingSalesImportRecord:
        record = TradingSalesImportRecord(**values)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def update_record(self, record: TradingSalesImportRecord, **values) -> TradingSalesImportRecord:
        for key, value in values.items():
            if value is not None:
                setattr(record, key, value)

        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_document(
        self,
        *,
        record_id: int,
        document_type: TradingImportDocumentType,
    ) -> TradingSalesDocument | None:
        statement = select(TradingSalesDocument).where(
            TradingSalesDocument.record_id == record_id,
            TradingSalesDocument.document_type == document_type,
        )
        return self.db.scalar(statement)

    def upsert_document(
        self,
        *,
        record_id: int,
        document_type: TradingImportDocumentType,
        values: dict,
    ) -> TradingSalesDocument:
        document = self.get_document(record_id=record_id, document_type=document_type)
        if document is None:
            document = TradingSalesDocument(record_id=record_id, document_type=document_type, **values)
        else:
            for key, value in values.items():
                setattr(document, key, value)

        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def get_form(
        self,
        *,
        record_id: int,
        document_type: TradingImportDocumentType,
    ) -> TradingSalesForm | None:
        statement = select(TradingSalesForm).where(
            TradingSalesForm.record_id == record_id,
            TradingSalesForm.document_type == document_type,
        )
        return self.db.scalar(statement)

    def upsert_form(
        self,
        *,
        record_id: int,
        document_type: TradingImportDocumentType,
        values: dict,
    ) -> TradingSalesForm:
        form = self.get_form(record_id=record_id, document_type=document_type)
        if form is None:
            form = TradingSalesForm(record_id=record_id, document_type=document_type, **values)
        else:
            for key, value in values.items():
                setattr(form, key, value)

        self.db.add(form)
        self.db.commit()
        self.db.refresh(form)
        return form

    def upsert_freight_invoice(
        self,
        *,
        record_id: int,
        values: dict,
    ) -> TradingSalesFreightInvoice:
        statement = select(TradingSalesFreightInvoice).where(TradingSalesFreightInvoice.record_id == record_id)
        invoice = self.db.scalar(statement)
        if invoice is None:
            invoice = TradingSalesFreightInvoice(record_id=record_id, **values)
        else:
            for key, value in values.items():
                setattr(invoice, key, value)

        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def create_payment_receipt(self, **values) -> TradingSalesPaymentReceipt:
        receipt = TradingSalesPaymentReceipt(**values)
        self.db.add(receipt)
        self.db.commit()
        self.db.refresh(receipt)
        return receipt

    def upsert_detention_invoice(
        self,
        *,
        record_id: int,
        values: dict,
    ) -> TradingSalesDetentionInvoice:
        statement = select(TradingSalesDetentionInvoice).where(TradingSalesDetentionInvoice.record_id == record_id)
        invoice = self.db.scalar(statement)
        if invoice is None:
            invoice = TradingSalesDetentionInvoice(record_id=record_id, **values)
        else:
            for key, value in values.items():
                setattr(invoice, key, value)

        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)
        return invoice
