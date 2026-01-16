# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FGN Savings Bond Subscription Application - A Python/Streamlit web application for submitting Federal Government of Nigeria Savings Bond applications. Digitizes the official DMO FGNSB subscription form process.

## Build & Run Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run main user app (port 8501)
streamlit run src/streamlit_app.py

# Run admin dashboard (port 8502)
streamlit run src/admin_app.py

# Docker deployment
docker-compose up -d
# Main app: http://localhost:8501
# Admin app: http://localhost:8502
```

## Architecture

### Dual Application Pattern
- **src/streamlit_app.py** - User-facing bond subscription form (dark theme)
- **src/admin_app.py** - Password-protected admin dashboard with analytics (light theme)

### Design System (`src/design_system/`)
Centralized design tokens and theming:
- **tokens.py** - Colors, typography, spacing, shadows, border-radius constants
- **theme.py** - Theme application functions (`apply_theme("dark")` or `apply_theme("light")`)
- DMO Green palette: `#006400` (primary), `#4CAF50` (accent)

### PDF Generation (`src/pdf/`)
Professional PDF generation matching official DMO form:
- **styles.py** - PDF colors and table styles (green theme)
- **elements.py** - Custom elements (CheckboxField, InputBoxes, SectionHeader, StampArea)
- **templates.py** - FGNSBTemplate class for DMO-styled form layout
- **generator.py** - High-level PDFGenerator interface

### UI Components (`src/components/`)
Reusable Streamlit components:
- **wizard.py** - FormWizard class for multi-step form navigation
- **progress.py** - Step progress indicator
- **form_fields.py** - Validated inputs (email, phone, BVN, currency)
- **feedback.py** - Loading spinners, success/error messages

### Core Modules
- **src/form_handler.py** - FormHandler class for validation and MongoDB management
- **src/utils.py** - Number-to-words conversion and money formatting

### Data Layer
- Primary: MongoDB (configured via environment variables)
- Fallback: Local JSON files in `data/` directory when MongoDB unavailable

### Reference PDF
- **FGNSB_Subscription_Form.05.pdf** - Official DMO form (PDF output should match this)

## Applicant Types
Three applicant types with different form structures:
- Individual (personal details, CSCS/CHN numbers)
- Joint (primary + secondary applicant)
- Corporate (company details, RC number)

## Key Dependencies
- Streamlit 1.31.1 (web framework)
- pymongo 4.6.1 (database)
- ReportLab 4.0.9 (PDF generation)
- Pandas/Plotly (analytics)

## Configuration

Environment variables in `.env`:
- `MONGODB_URI` - Database connection string
- `ADMIN_PASSWORD_HASH` - Admin authentication
- `ENVIRONMENT` - development/production

Streamlit config in `.streamlit/config.toml`:
- DMO green theme colors
- Server settings
