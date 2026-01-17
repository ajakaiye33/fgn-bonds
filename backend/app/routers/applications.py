"""Applications API router - Form submission and PDF generation."""

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.application import Application
from ..schemas.application import ApplicationCreate, ApplicationResponse
from ..services.pdf import generate_application_pdf

logger = structlog.get_logger()

router = APIRouter()


@router.post(
    "/applications",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_application(
    application: ApplicationCreate,
    db: Session = Depends(get_db),
):
    """
    Submit a new bond subscription application.

    Creates the application record in the database and returns the created application
    with its ID, which can be used to generate the PDF.
    """
    logger.info(
        "Creating new application",
        applicant_type=application.applicant_type,
        bond_value=application.bond_value,
    )

    # Create database record
    db_application = Application(**application.model_dump())
    db.add(db_application)
    db.commit()
    db.refresh(db_application)

    logger.info(
        "Application created successfully",
        application_id=db_application.id,
    )

    return db_application


@router.get("/applications/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: int,
    db: Session = Depends(get_db),
):
    """Get a specific application by ID."""
    application = db.query(Application).filter(Application.id == application_id).first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with ID {application_id} not found",
        )

    return application


@router.get("/applications/{application_id}/pdf")
async def download_application_pdf(
    application_id: int,
    db: Session = Depends(get_db),
):
    """
    Generate and download the PDF for an application.

    Returns the official DMO-styled subscription form PDF.
    """
    application = db.query(Application).filter(Application.id == application_id).first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with ID {application_id} not found",
        )

    logger.info("Generating PDF", application_id=application_id)

    try:
        pdf_path = generate_application_pdf(application)

        # Determine filename based on applicant type
        if application.applicant_type == "Corporate":
            name = application.company_name or "company"
        else:
            name = application.full_name or "applicant"

        filename = f"FGNSB_Subscription_{name.replace(' ', '_')}.pdf"

        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename=filename,
        )
    except Exception as e:
        logger.exception("PDF generation failed", application_id=application_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF: {str(e)}",
        )
