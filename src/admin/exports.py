"""
Export Manager

Enhanced export functionality for CSV, Excel, and PDF reports.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, List, Any
import tempfile
import io


class ExportManager:
    """
    Manages data exports in various formats.
    """

    def __init__(self, df: pd.DataFrame, title: str = "Bond Applications"):
        """
        Initialize the export manager.

        Args:
            df: DataFrame to export
            title: Title for the export
        """
        self.df = df.copy()
        self.title = title
        self.timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    def render_export_buttons(self, key_prefix: str = "export"):
        """
        Render export buttons in the UI.

        Args:
            key_prefix: Prefix for button keys
        """
        if self.df.empty:
            st.info("No data to export.")
            return

        st.subheader("Export Data")

        col1, col2, col3 = st.columns(3)

        with col1:
            csv_data = self.to_csv()
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name=f"{self.title.lower().replace(' ', '_')}_{self.timestamp}.csv",
                mime="text/csv",
                key=f"{key_prefix}_csv",
                use_container_width=True,
            )

        with col2:
            excel_data = self.to_excel()
            st.download_button(
                label="Download Excel",
                data=excel_data,
                file_name=f"{self.title.lower().replace(' ', '_')}_{self.timestamp}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"{key_prefix}_excel",
                use_container_width=True,
            )

        with col3:
            pdf_data = self.to_pdf_report()
            if pdf_data:
                st.download_button(
                    label="Download PDF Report",
                    data=pdf_data,
                    file_name=f"{self.title.lower().replace(' ', '_')}_report_{self.timestamp}.pdf",
                    mime="application/pdf",
                    key=f"{key_prefix}_pdf",
                    use_container_width=True,
                )
            else:
                st.button(
                    "PDF Not Available",
                    disabled=True,
                    key=f"{key_prefix}_pdf_disabled",
                    use_container_width=True,
                )

    def to_csv(self, **kwargs) -> bytes:
        """
        Export DataFrame to CSV.

        Args:
            **kwargs: Additional arguments for to_csv

        Returns:
            CSV data as bytes
        """
        return export_to_csv(self.df, **kwargs)

    def to_excel(
        self,
        sheet_name: str = "Data",
        include_summary: bool = True,
        **kwargs
    ) -> bytes:
        """
        Export DataFrame to Excel with optional summary sheet.

        Args:
            sheet_name: Name for the data sheet
            include_summary: Whether to include a summary sheet
            **kwargs: Additional arguments

        Returns:
            Excel data as bytes
        """
        return export_to_excel(
            self.df,
            sheet_name=sheet_name,
            include_summary=include_summary,
            title=self.title,
            **kwargs
        )

    def to_pdf_report(self) -> Optional[bytes]:
        """
        Export DataFrame as a PDF report.

        Returns:
            PDF data as bytes, or None if generation fails
        """
        return export_to_pdf_report(self.df, self.title)


def export_to_csv(
    df: pd.DataFrame,
    format_currency: bool = True,
    date_format: str = '%Y-%m-%d %H:%M:%S',
    **kwargs
) -> bytes:
    """
    Export DataFrame to CSV with formatting.

    Args:
        df: DataFrame to export
        format_currency: Whether to format currency columns
        date_format: Date format string
        **kwargs: Additional pandas to_csv arguments

    Returns:
        CSV data as bytes
    """
    export_df = df.copy()

    # Format bond_value as currency if present
    if format_currency and 'bond_value' in export_df.columns:
        export_df['bond_value_formatted'] = export_df['bond_value'].apply(
            lambda x: f"₦{x:,.2f}" if pd.notna(x) else ''
        )

    # Convert to CSV
    csv_buffer = io.StringIO()
    export_df.to_csv(csv_buffer, index=False, **kwargs)
    return csv_buffer.getvalue().encode('utf-8')


def export_to_excel(
    df: pd.DataFrame,
    sheet_name: str = "Data",
    include_summary: bool = True,
    title: str = "Bond Applications",
    **kwargs
) -> bytes:
    """
    Export DataFrame to Excel with multiple sheets.

    Args:
        df: DataFrame to export
        sheet_name: Name for the data sheet
        include_summary: Whether to include a summary sheet
        title: Report title for summary
        **kwargs: Additional arguments

    Returns:
        Excel data as bytes
    """
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Main data sheet
        export_df = df.copy()

        # Format bond_value column if present
        if 'bond_value' in export_df.columns:
            export_df['Bond Value (Formatted)'] = export_df['bond_value'].apply(
                lambda x: f"₦{x:,.2f}" if pd.notna(x) else ''
            )

        export_df.to_excel(writer, sheet_name=sheet_name, index=False)

        # Summary sheet
        if include_summary and not df.empty:
            summary_data = _generate_summary_data(df, title)
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name="Summary", index=False)

            # Breakdown by type if available
            if 'applicant_type' in df.columns:
                type_summary = df.groupby('applicant_type').agg({
                    'bond_value': ['count', 'sum', 'mean']
                }).reset_index()
                type_summary.columns = ['Applicant Type', 'Count', 'Total Value', 'Average Value']
                type_summary['Total Value'] = type_summary['Total Value'].apply(lambda x: f"₦{x:,.2f}")
                type_summary['Average Value'] = type_summary['Average Value'].apply(lambda x: f"₦{x:,.2f}")
                type_summary.to_excel(writer, sheet_name="By Type", index=False)

            # Breakdown by month if available
            if 'month_of_offer' in df.columns:
                month_summary = df.groupby('month_of_offer').agg({
                    'bond_value': ['count', 'sum']
                }).reset_index()
                month_summary.columns = ['Month', 'Count', 'Total Value']
                month_summary['Total Value'] = month_summary['Total Value'].apply(lambda x: f"₦{x:,.2f}")
                month_summary.to_excel(writer, sheet_name="By Month", index=False)

    output.seek(0)
    return output.getvalue()


def _generate_summary_data(df: pd.DataFrame, title: str) -> List[Dict[str, Any]]:
    """Generate summary statistics for Excel export."""
    summary = [
        {"Metric": "Report Title", "Value": title},
        {"Metric": "Generated On", "Value": datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
        {"Metric": "", "Value": ""},
        {"Metric": "Total Applications", "Value": len(df)},
    ]

    if 'bond_value' in df.columns:
        total_value = df['bond_value'].sum()
        avg_value = df['bond_value'].mean() if len(df) > 0 else 0
        min_value = df['bond_value'].min() if len(df) > 0 else 0
        max_value = df['bond_value'].max() if len(df) > 0 else 0

        summary.extend([
            {"Metric": "Total Bond Value", "Value": f"₦{total_value:,.2f}"},
            {"Metric": "Average Bond Value", "Value": f"₦{avg_value:,.2f}"},
            {"Metric": "Minimum Bond Value", "Value": f"₦{min_value:,.2f}"},
            {"Metric": "Maximum Bond Value", "Value": f"₦{max_value:,.2f}"},
        ])

    if 'applicant_type' in df.columns:
        summary.append({"Metric": "", "Value": ""})
        summary.append({"Metric": "Applications by Type", "Value": ""})
        for app_type, count in df['applicant_type'].value_counts().items():
            summary.append({"Metric": f"  - {app_type}", "Value": count})

    if 'tenor' in df.columns:
        summary.append({"Metric": "", "Value": ""})
        summary.append({"Metric": "Applications by Tenor", "Value": ""})
        for tenor, count in df['tenor'].value_counts().items():
            summary.append({"Metric": f"  - {tenor}", "Value": count})

    return summary


def export_to_pdf_report(df: pd.DataFrame, title: str = "Bond Applications Report") -> Optional[bytes]:
    """
    Export DataFrame as a PDF summary report.

    Args:
        df: DataFrame to export
        title: Report title

    Returns:
        PDF data as bytes, or None if ReportLab is not available
    """
    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm, inch
        from reportlab.platypus import (
            SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        )
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    except ImportError:
        return None

    if df.empty:
        return None

    # Create PDF buffer
    buffer = io.BytesIO()

    # Create document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=15*mm,
        rightMargin=15*mm,
        topMargin=15*mm,
        bottomMargin=15*mm,
    )

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=20,
        textColor=colors.HexColor('#006400'),
    )
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10,
        textColor=colors.HexColor('#006400'),
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=10,
    )
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_CENTER,
        textColor=colors.gray,
    )

    elements = []

    # Title
    elements.append(Paragraph(title, title_style))
    elements.append(Paragraph(
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        footer_style
    ))
    elements.append(Spacer(1, 20))

    # Summary statistics
    elements.append(Paragraph("Summary Statistics", heading_style))

    total_apps = len(df)
    total_value = df['bond_value'].sum() if 'bond_value' in df.columns else 0
    avg_value = df['bond_value'].mean() if 'bond_value' in df.columns and total_apps > 0 else 0

    summary_data = [
        ["Metric", "Value"],
        ["Total Applications", str(total_apps)],
        ["Total Bond Value", f"₦{total_value:,.2f}"],
        ["Average Bond Value", f"₦{avg_value:,.2f}"],
    ]

    summary_table = Table(summary_data, colWidths=[150, 150])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#006400')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#006400')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 20))

    # Breakdown by applicant type
    if 'applicant_type' in df.columns:
        elements.append(Paragraph("Applications by Type", heading_style))

        type_data = [["Applicant Type", "Count", "Total Value", "Percentage"]]
        type_counts = df.groupby('applicant_type').agg({
            'bond_value': ['count', 'sum']
        }).reset_index()

        for _, row in type_counts.iterrows():
            app_type = row['applicant_type']
            count = row[('bond_value', 'count')]
            value = row[('bond_value', 'sum')]
            pct = (count / total_apps * 100) if total_apps > 0 else 0
            type_data.append([
                app_type,
                str(count),
                f"₦{value:,.2f}",
                f"{pct:.1f}%"
            ])

        type_table = Table(type_data, colWidths=[100, 60, 120, 80])
        type_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#006400')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#006400')),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(type_table)
        elements.append(Spacer(1, 20))

    # Breakdown by tenor
    if 'tenor' in df.columns:
        elements.append(Paragraph("Applications by Tenor", heading_style))

        tenor_data = [["Tenor", "Count", "Total Value"]]
        tenor_counts = df.groupby('tenor').agg({
            'bond_value': ['count', 'sum']
        }).reset_index()

        for _, row in tenor_counts.iterrows():
            tenor = row['tenor']
            count = row[('bond_value', 'count')]
            value = row[('bond_value', 'sum')]
            tenor_data.append([
                tenor,
                str(count),
                f"₦{value:,.2f}"
            ])

        tenor_table = Table(tenor_data, colWidths=[100, 80, 120])
        tenor_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#006400')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#006400')),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(tenor_table)
        elements.append(Spacer(1, 20))

    # Footer
    elements.append(Spacer(1, 30))
    elements.append(Paragraph(
        "FGN Savings Bond Subscription System - Administrative Report",
        footer_style
    ))

    # Build PDF
    doc.build(elements)

    buffer.seek(0)
    return buffer.getvalue()
