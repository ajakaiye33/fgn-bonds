"""Admin API router - Dashboard analytics, filtering, exports, and payment management."""

import io
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Annotated

import pandas as pd
import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

# Configure upload directory
UPLOAD_DIR = Path("/app/uploads/payment_documents")
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

from ..database import get_db
from ..models.application import Application
from ..models.payment import Payment, PaymentDocument
from ..routers.auth import TokenData, get_current_user
from ..schemas.admin import (
    AdminFilters,
    AnalyticsResponse,
    ApplicationListResponse,
    SummaryResponse,
)
from ..schemas.payment import (
    DMOSubmissionCreate,
    DMOSubmissionResponse,
    MonthlyReportSummary,
    PaymentCreate,
    PaymentDocumentResponse,
    PaymentResponse,
    PaymentUpdate,
    PaymentVerify,
)
from ..models.payment import DMOSubmission
from ..utils.constants import BOND_VALUE_RANGES

logger = structlog.get_logger()

router = APIRouter()


def apply_filters(query, filters: AdminFilters):
    """Apply filters to the applications query."""
    if filters.applicant_types:
        query = query.filter(Application.applicant_type.in_(filters.applicant_types))

    if filters.tenors:
        query = query.filter(Application.tenor.in_(filters.tenors))

    if filters.start_date:
        query = query.filter(Application.submission_date >= filters.start_date)

    if filters.end_date:
        query = query.filter(Application.submission_date <= filters.end_date)

    if filters.min_value is not None:
        query = query.filter(Application.bond_value >= filters.min_value)

    if filters.max_value is not None:
        query = query.filter(Application.bond_value <= filters.max_value)

    if filters.is_resident is not None:
        query = query.filter(Application.is_resident == filters.is_resident)

    if filters.payment_statuses:
        query = query.filter(Application.payment_status.in_(filters.payment_statuses))

    if filters.search:
        search_term = f"%{filters.search}%"
        query = query.filter(
            (Application.full_name.ilike(search_term))
            | (Application.company_name.ilike(search_term))
            | (Application.email.ilike(search_term))
            | (Application.phone_number.ilike(search_term))
        )

    return query


@router.get("/applications", response_model=ApplicationListResponse)
async def list_applications(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: Annotated[int, Query(ge=0)] = 0,
    page_size: Annotated[int, Query(ge=10, le=250)] = 25,
    applicant_types: list[str] | None = Query(None),
    tenors: list[str] | None = Query(None),
    start_date: str | None = None,
    end_date: str | None = None,
    min_value: float | None = None,
    max_value: float | None = None,
    is_resident: bool | None = None,
    payment_statuses: list[str] | None = Query(None),
    search: str | None = None,
):
    """
    List applications with filtering and pagination.

    Admin-only endpoint.
    """
    filters = AdminFilters(
        applicant_types=applicant_types,
        tenors=tenors,
        start_date=start_date,
        end_date=end_date,
        min_value=min_value,
        max_value=max_value,
        is_resident=is_resident,
        payment_statuses=payment_statuses,
        search=search,
    )

    query = db.query(Application)
    query = apply_filters(query, filters)

    # Get total count
    total = query.count()

    # Apply pagination
    applications = (
        query.order_by(Application.submission_date.desc())
        .offset(page * page_size)
        .limit(page_size)
        .all()
    )

    return ApplicationListResponse(
        items=applications,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/summary", response_model=SummaryResponse)
async def get_summary(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get dashboard summary metrics.

    Returns total applications, total value, average value, and monthly counts.
    """
    # Total applications
    total_applications = db.query(func.count(Application.id)).scalar()

    # Total and average bond value
    total_value = db.query(func.sum(Application.bond_value)).scalar() or 0
    avg_value = db.query(func.avg(Application.bond_value)).scalar() or 0

    # This month's applications
    now = datetime.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    this_month_count = (
        db.query(func.count(Application.id))
        .filter(Application.created_at >= month_start.isoformat())
        .scalar()
    )

    # By applicant type
    by_type = (
        db.query(Application.applicant_type, func.count(Application.id))
        .group_by(Application.applicant_type)
        .all()
    )
    by_type_dict = {t: c for t, c in by_type}

    return SummaryResponse(
        total_applications=total_applications,
        total_value=total_value,
        average_value=avg_value,
        this_month_count=this_month_count,
        by_applicant_type=by_type_dict,
    )


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get analytics data for charts.

    Returns data for:
    - Applications by type
    - Applications by month
    - Value distribution
    - Daily trends
    """
    # By applicant type
    by_type = (
        db.query(
            Application.applicant_type,
            func.count(Application.id).label("count"),
            func.sum(Application.bond_value).label("total_value"),
        )
        .group_by(Application.applicant_type)
        .all()
    )

    # By month of offer
    by_month = (
        db.query(
            Application.month_of_offer,
            func.count(Application.id).label("count"),
            func.sum(Application.bond_value).label("total_value"),
        )
        .group_by(Application.month_of_offer)
        .all()
    )

    # By tenor
    by_tenor = (
        db.query(
            Application.tenor,
            func.count(Application.id).label("count"),
            func.sum(Application.bond_value).label("total_value"),
        )
        .group_by(Application.tenor)
        .all()
    )

    # Value distribution
    all_values = db.query(Application.bond_value).all()
    value_distribution = []
    for min_val, max_val, label in BOND_VALUE_RANGES:
        count = sum(1 for (v,) in all_values if min_val <= v < max_val)
        value_distribution.append({"range": label, "count": count})

    return AnalyticsResponse(
        by_applicant_type=[
            {"type": t, "count": c, "total_value": v or 0} for t, c, v in by_type
        ],
        by_month=[
            {"month": m, "count": c, "total_value": v or 0} for m, c, v in by_month
        ],
        by_tenor=[
            {"tenor": t, "count": c, "total_value": v or 0} for t, c, v in by_tenor
        ],
        value_distribution=value_distribution,
    )


@router.get("/export/csv")
async def export_csv(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
    applicant_types: list[str] | None = Query(None),
    tenors: list[str] | None = Query(None),
    start_date: str | None = None,
    end_date: str | None = None,
):
    """Export filtered applications to CSV."""
    filters = AdminFilters(
        applicant_types=applicant_types,
        tenors=tenors,
        start_date=start_date,
        end_date=end_date,
    )

    query = db.query(Application)
    query = apply_filters(query, filters)
    applications = query.all()

    # Convert to DataFrame
    data = [app.__dict__ for app in applications]
    for d in data:
        d.pop("_sa_instance_state", None)

    df = pd.DataFrame(data)

    # Generate CSV
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=fgn_bonds_export_{datetime.now().strftime('%Y%m%d')}.csv"
        },
    )


@router.get("/export/excel")
async def export_excel(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
    applicant_types: list[str] | None = Query(None),
    tenors: list[str] | None = Query(None),
    start_date: str | None = None,
    end_date: str | None = None,
):
    """Export filtered applications to Excel with summary sheet."""
    filters = AdminFilters(
        applicant_types=applicant_types,
        tenors=tenors,
        start_date=start_date,
        end_date=end_date,
    )

    query = db.query(Application)
    query = apply_filters(query, filters)
    applications = query.all()

    # Convert to DataFrame
    data = [app.__dict__ for app in applications]
    for d in data:
        d.pop("_sa_instance_state", None)

    df = pd.DataFrame(data)

    # Generate Excel with multiple sheets
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # Data sheet
        df.to_excel(writer, sheet_name="Applications", index=False)

        # Summary sheet
        summary_data = {
            "Metric": [
                "Total Applications",
                "Total Value",
                "Average Value",
                "Min Value",
                "Max Value",
            ],
            "Value": [
                len(df),
                df["bond_value"].sum() if not df.empty else 0,
                df["bond_value"].mean() if not df.empty else 0,
                df["bond_value"].min() if not df.empty else 0,
                df["bond_value"].max() if not df.empty else 0,
            ],
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name="Summary", index=False)

        # By Type sheet
        if not df.empty:
            by_type = df.groupby("applicant_type").agg(
                Count=("id", "count"), Total_Value=("bond_value", "sum")
            )
            by_type.to_excel(writer, sheet_name="By Type")

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=fgn_bonds_export_{datetime.now().strftime('%Y%m%d')}.xlsx"
        },
    )


# =============================================================================
# PAYMENT MANAGEMENT ENDPOINTS
# =============================================================================


@router.post("/applications/{application_id}/payment", response_model=PaymentResponse)
async def record_payment(
    application_id: int,
    payment_data: PaymentCreate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Record a payment for an application.

    This is called when a subscriber pays for their bond subscription.
    The payment_reference (deposit/transfer reference) is critical for DMO reconciliation.
    """
    # Check if application exists
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application {application_id} not found",
        )

    # Check if payment already exists for this application
    existing_payment = (
        db.query(Payment).filter(Payment.application_id == application_id).first()
    )
    if existing_payment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment already exists for application {application_id}. Use PATCH to update.",
        )

    # Create payment record
    payment = Payment(
        application_id=application_id,
        amount=int(payment_data.amount * 100),  # Convert Naira to kobo
        payment_method=payment_data.payment_method,
        payment_reference=payment_data.payment_reference,
        payment_date=payment_data.payment_date,
        receiving_bank=payment_data.receiving_bank,
        notes=payment_data.notes,
        status="pending",
    )
    db.add(payment)

    # Update application payment_status to "paid"
    application.payment_status = "paid"

    db.commit()
    db.refresh(payment)

    logger.info(
        "payment_recorded",
        application_id=application_id,
        payment_id=payment.id,
        payment_reference=payment.payment_reference,
        amount=payment_data.amount,
        user=current_user.username,
    )

    return payment


@router.get("/applications/{application_id}/payment", response_model=PaymentResponse)
async def get_application_payment(
    application_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get payment details for an application."""
    payment = (
        db.query(Payment).filter(Payment.application_id == application_id).first()
    )
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No payment found for application {application_id}",
        )
    return payment


@router.patch("/payments/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: int,
    payment_data: PaymentUpdate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update payment details."""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment {payment_id} not found",
        )

    # Can only update pending payments
    if payment.status == "verified":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update a verified payment",
        )

    # Update fields that were provided
    update_data = payment_data.model_dump(exclude_unset=True)
    if "amount" in update_data:
        update_data["amount"] = int(update_data["amount"] * 100)  # Convert to kobo

    for key, value in update_data.items():
        setattr(payment, key, value)

    payment.updated_at = datetime.now().isoformat()
    db.commit()
    db.refresh(payment)

    logger.info(
        "payment_updated",
        payment_id=payment_id,
        updates=list(update_data.keys()),
        user=current_user.username,
    )

    return payment


@router.post("/payments/{payment_id}/verify", response_model=PaymentResponse)
async def verify_payment(
    payment_id: int,
    verification: PaymentVerify,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Verify or reject a payment.

    - action: "verify" marks payment as verified and ready for DMO report
    - action: "reject" marks payment as rejected (requires rejection_reason)
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment {payment_id} not found",
        )

    if payment.status == "verified" and verification.action == "verify":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment is already verified",
        )

    # Get the associated application
    application = (
        db.query(Application).filter(Application.id == payment.application_id).first()
    )

    if verification.action == "verify":
        payment.status = "verified"
        payment.verified_at = datetime.now().isoformat()
        payment.verified_by = current_user.username
        payment.rejection_reason = None
        if application:
            application.payment_status = "verified"

        logger.info(
            "payment_verified",
            payment_id=payment_id,
            application_id=payment.application_id,
            user=current_user.username,
        )

    elif verification.action == "reject":
        payment.status = "rejected"
        payment.rejection_reason = verification.rejection_reason
        payment.verified_at = None
        payment.verified_by = None
        if application:
            application.payment_status = "rejected"

        logger.info(
            "payment_rejected",
            payment_id=payment_id,
            application_id=payment.application_id,
            reason=verification.rejection_reason,
            user=current_user.username,
        )

    payment.updated_at = datetime.now().isoformat()
    db.commit()
    db.refresh(payment)

    return payment


@router.delete("/payments/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(
    payment_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a payment record.

    Only pending or rejected payments can be deleted.
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment {payment_id} not found",
        )

    if payment.status == "verified":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a verified payment",
        )

    # Reset application payment_status to pending
    application = (
        db.query(Application).filter(Application.id == payment.application_id).first()
    )
    if application:
        application.payment_status = "pending"

    db.delete(payment)
    db.commit()

    logger.info(
        "payment_deleted",
        payment_id=payment_id,
        application_id=payment.application_id if payment else None,
        user=current_user.username,
    )


# =============================================================================
# DOCUMENT UPLOAD ENDPOINTS
# =============================================================================


def validate_file(file: UploadFile) -> None:
    """Validate uploaded file type and size."""
    # Check extension
    ext = Path(file.filename).suffix.lower() if file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Check content type
    allowed_content_types = {
        "application/pdf",
        "image/jpeg",
        "image/jpg",
        "image/png",
    }
    if file.content_type not in allowed_content_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid content type: {file.content_type}",
        )


@router.post(
    "/payments/{payment_id}/documents",
    response_model=PaymentDocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_payment_document(
    payment_id: int,
    file: UploadFile,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload a payment evidence document.

    Supports PDF, JPG, JPEG, PNG files up to 5MB.
    """
    # Check payment exists
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment {payment_id} not found",
        )

    # Validate file
    validate_file(file)

    # Read file content
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024 * 1024)}MB",
        )

    # Create upload directory if needed
    payment_dir = UPLOAD_DIR / str(payment_id)
    payment_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    ext = Path(file.filename).suffix.lower() if file.filename else ".pdf"
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = payment_dir / unique_filename

    # Save file
    with open(file_path, "wb") as f:
        f.write(content)

    # Create database record
    document = PaymentDocument(
        payment_id=payment_id,
        filename=unique_filename,
        original_filename=file.filename or "document",
        file_path=str(file_path),
        file_size=len(content),
        mime_type=file.content_type,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    logger.info(
        "document_uploaded",
        payment_id=payment_id,
        document_id=document.id,
        filename=file.filename,
        size=len(content),
        user=current_user.username,
    )

    return document


@router.get(
    "/payments/{payment_id}/documents",
    response_model=list[PaymentDocumentResponse],
)
async def list_payment_documents(
    payment_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all documents for a payment."""
    # Check payment exists
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment {payment_id} not found",
        )

    documents = (
        db.query(PaymentDocument)
        .filter(PaymentDocument.payment_id == payment_id)
        .order_by(PaymentDocument.uploaded_at.desc())
        .all()
    )
    return documents


@router.get("/documents/{document_id}/download")
async def download_document(
    document_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download a payment evidence document."""
    document = db.query(PaymentDocument).filter(PaymentDocument.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found",
        )

    file_path = Path(document.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document file not found on disk",
        )

    return FileResponse(
        path=str(file_path),
        filename=document.original_filename,
        media_type=document.mime_type or "application/octet-stream",
    )


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a payment evidence document."""
    document = db.query(PaymentDocument).filter(PaymentDocument.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found",
        )

    # Check if payment is verified - can't delete verified payment documents
    payment = db.query(Payment).filter(Payment.id == document.payment_id).first()
    if payment and payment.status == "verified":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete documents from a verified payment",
        )

    # Delete file from disk
    file_path = Path(document.file_path)
    if file_path.exists():
        os.remove(file_path)

    # Delete database record
    db.delete(document)
    db.commit()

    logger.info(
        "document_deleted",
        document_id=document_id,
        payment_id=document.payment_id,
        filename=document.original_filename,
        user=current_user.username,
    )


# =============================================================================
# DMO REPORTING ENDPOINTS
# =============================================================================


@router.get("/reports/monthly-summary", response_model=MonthlyReportSummary)
async def get_monthly_report_summary(
    month_of_offer: str = Query(..., description="Month name (e.g., 'January')"),
    year: int = Query(..., ge=2020, le=2100),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get summary statistics for a monthly DMO report.

    Returns totals, breakdowns by tenor/type/payment status, and submission status.
    """
    # Base query for the month
    base_query = db.query(Application).filter(
        Application.month_of_offer == month_of_offer,
        # Extract year from submission_date
        func.substr(Application.submission_date, 1, 4) == str(year),
    )

    # Total applications and value
    total_apps = base_query.count()
    total_value = base_query.with_entities(func.sum(Application.bond_value)).scalar() or 0

    if total_apps == 0:
        return MonthlyReportSummary(
            month_of_offer=month_of_offer,
            year=year,
            total_applications=0,
            total_value=0,
            average_value=0,
            total_2year=0,
            value_2year=0,
            total_3year=0,
            value_3year=0,
            total_individual=0,
            total_joint=0,
            total_corporate=0,
            pending_count=0,
            pending_value=0,
            paid_count=0,
            paid_value=0,
            verified_count=0,
            verified_value=0,
            rejected_count=0,
            rejected_value=0,
            is_submitted=False,
        )

    # By tenor
    tenor_stats = (
        base_query.with_entities(
            Application.tenor,
            func.count(Application.id),
            func.sum(Application.bond_value),
        )
        .group_by(Application.tenor)
        .all()
    )
    tenor_dict = {t: (c, v or 0) for t, c, v in tenor_stats}

    # By applicant type
    type_stats = (
        base_query.with_entities(Application.applicant_type, func.count(Application.id))
        .group_by(Application.applicant_type)
        .all()
    )
    type_dict = {t: c for t, c in type_stats}

    # By payment status
    payment_stats = (
        base_query.with_entities(
            Application.payment_status,
            func.count(Application.id),
            func.sum(Application.bond_value),
        )
        .group_by(Application.payment_status)
        .all()
    )
    payment_dict = {s: (c, v or 0) for s, c, v in payment_stats}

    # Check if submitted
    submission = (
        db.query(DMOSubmission)
        .filter(
            DMOSubmission.month_of_offer == month_of_offer,
            DMOSubmission.year == year,
        )
        .first()
    )

    return MonthlyReportSummary(
        month_of_offer=month_of_offer,
        year=year,
        total_applications=total_apps,
        total_value=total_value,
        average_value=total_value / total_apps if total_apps > 0 else 0,
        total_2year=tenor_dict.get("2-Year", (0, 0))[0],
        value_2year=tenor_dict.get("2-Year", (0, 0))[1],
        total_3year=tenor_dict.get("3-Year", (0, 0))[0],
        value_3year=tenor_dict.get("3-Year", (0, 0))[1],
        total_individual=type_dict.get("Individual", 0),
        total_joint=type_dict.get("Joint", 0),
        total_corporate=type_dict.get("Corporate", 0),
        pending_count=payment_dict.get("pending", (0, 0))[0],
        pending_value=payment_dict.get("pending", (0, 0))[1],
        paid_count=payment_dict.get("paid", (0, 0))[0],
        paid_value=payment_dict.get("paid", (0, 0))[1],
        verified_count=payment_dict.get("verified", (0, 0))[0],
        verified_value=payment_dict.get("verified", (0, 0))[1],
        rejected_count=payment_dict.get("rejected", (0, 0))[0],
        rejected_value=payment_dict.get("rejected", (0, 0))[1],
        is_submitted=submission is not None,
        submission_id=submission.id if submission else None,
        submitted_at=submission.submitted_at if submission else None,
    )


@router.get("/reports/export/excel")
async def export_dmo_report_excel(
    month_of_offer: str = Query(..., description="Month name (e.g., 'January')"),
    year: int = Query(..., ge=2020, le=2100),
    include_pending: bool = Query(False, description="Include pending payments"),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Export DMO monthly report as Excel file.

    Contains summary sheet and detailed applications sheet with payment info.
    """
    # Build query
    query = (
        db.query(Application)
        .outerjoin(Payment, Application.id == Payment.application_id)
        .filter(
            Application.month_of_offer == month_of_offer,
            func.substr(Application.submission_date, 1, 4) == str(year),
        )
    )

    if not include_pending:
        query = query.filter(Application.payment_status == "verified")

    applications = query.all()

    # Build dataframe for detailed applications
    data = []
    for app in applications:
        # Determine applicant name based on type
        if app.applicant_type == "Corporate":
            applicant_name = app.company_name
        else:
            applicant_name = app.full_name

        row = {
            "S/N": len(data) + 1,
            "Applicant Name": applicant_name,
            "Applicant Type": app.applicant_type,
            "BVN": app.bvn,
            "Tenor": app.tenor,
            "Bond Value (₦)": app.bond_value,
            "Bank Name": app.bank_name,
            "Account Number": app.account_number,
            "Payment Status": app.payment_status,
        }

        # Add payment details if available
        if app.payment:
            row["Payment Reference"] = app.payment.payment_reference
            row["Payment Date"] = app.payment.payment_date
            row["Payment Method"] = app.payment.payment_method
            row["Amount Received (₦)"] = app.payment.amount / 100  # Convert from kobo
        else:
            row["Payment Reference"] = ""
            row["Payment Date"] = ""
            row["Payment Method"] = ""
            row["Amount Received (₦)"] = ""

        data.append(row)

    df = pd.DataFrame(data)

    # Calculate summary
    total_apps = len(applications)
    total_value = sum(app.bond_value for app in applications)
    verified_apps = [a for a in applications if a.payment_status == "verified"]
    verified_value = sum(a.bond_value for a in verified_apps)
    apps_2year = [a for a in applications if a.tenor == "2-Year"]
    apps_3year = [a for a in applications if a.tenor == "3-Year"]

    # Generate Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # Summary sheet
        summary_data = {
            "Metric": [
                "Report Period",
                "Total Applications",
                "Total Value (₦)",
                "",
                "2-Year Bonds",
                "2-Year Value (₦)",
                "3-Year Bonds",
                "3-Year Value (₦)",
                "",
                "Verified Payments",
                "Verified Value (₦)",
                "",
                "Report Generated",
            ],
            "Value": [
                f"{month_of_offer} {year}",
                total_apps,
                total_value,
                "",
                len(apps_2year),
                sum(a.bond_value for a in apps_2year),
                len(apps_3year),
                sum(a.bond_value for a in apps_3year),
                "",
                len(verified_apps),
                verified_value,
                "",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ],
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name="Summary", index=False)

        # Detailed applications sheet
        if not df.empty:
            df.to_excel(writer, sheet_name="Applications", index=False)

    output.seek(0)

    filename = f"DMO_Report_{month_of_offer}_{year}_{datetime.now().strftime('%Y%m%d')}.xlsx"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.post("/reports/submit-to-dmo", response_model=DMOSubmissionResponse)
async def mark_as_submitted_to_dmo(
    submission_data: DMOSubmissionCreate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Mark a month's applications as submitted to DMO.

    Creates an audit trail of when the report was generated and submitted.
    """
    # Check if already submitted
    existing = (
        db.query(DMOSubmission)
        .filter(
            DMOSubmission.month_of_offer == submission_data.month_of_offer,
            DMOSubmission.year == submission_data.year,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{submission_data.month_of_offer} {submission_data.year} has already been marked as submitted",
        )

    # Get statistics for the submission
    base_query = db.query(Application).filter(
        Application.month_of_offer == submission_data.month_of_offer,
        func.substr(Application.submission_date, 1, 4) == str(submission_data.year),
        Application.payment_status == "verified",
    )

    total_apps = base_query.count()
    total_value = base_query.with_entities(func.sum(Application.bond_value)).scalar() or 0

    # Count by tenor
    tenor_stats = (
        base_query.with_entities(Application.tenor, func.count(Application.id))
        .group_by(Application.tenor)
        .all()
    )
    tenor_dict = {t: c for t, c in tenor_stats}

    # Create submission record
    submission = DMOSubmission(
        month_of_offer=submission_data.month_of_offer,
        year=submission_data.year,
        total_applications=total_apps,
        total_value=int(total_value),  # Store as kobo
        total_2year=tenor_dict.get("2-Year", 0),
        total_3year=tenor_dict.get("3-Year", 0),
        total_verified=total_apps,
        submitted_by=current_user.username,
        notes=submission_data.notes,
    )
    db.add(submission)

    # Update applications to link to this submission
    base_query.update(
        {Application.dmo_submission_id: submission.id},
        synchronize_session=False,
    )

    db.commit()
    db.refresh(submission)

    logger.info(
        "dmo_submission_created",
        submission_id=submission.id,
        month=submission_data.month_of_offer,
        year=submission_data.year,
        total_applications=total_apps,
        total_value=total_value,
        user=current_user.username,
    )

    return submission


@router.get("/reports/submissions", response_model=list[DMOSubmissionResponse])
async def get_submission_history(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get history of DMO report submissions."""
    submissions = (
        db.query(DMOSubmission)
        .order_by(DMOSubmission.submitted_at.desc())
        .all()
    )
    return submissions
