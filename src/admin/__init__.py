"""
Admin Module

Enhanced admin dashboard components for the FGN Savings Bond application.
Provides advanced filtering, pagination, and export functionality.
"""

from .filters import (
    FilterPanel,
    FilterState,
    render_filter_panel,
    apply_filters,
)

from .pagination import (
    PaginatedTable,
    PaginationState,
    render_paginated_table,
)

from .exports import (
    ExportManager,
    export_to_csv,
    export_to_excel,
    export_to_pdf_report,
)

__all__ = [
    # Filters
    'FilterPanel',
    'FilterState',
    'render_filter_panel',
    'apply_filters',
    # Pagination
    'PaginatedTable',
    'PaginationState',
    'render_paginated_table',
    # Exports
    'ExportManager',
    'export_to_csv',
    'export_to_excel',
    'export_to_pdf_report',
]
