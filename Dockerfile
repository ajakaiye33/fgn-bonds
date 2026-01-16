# FGN Savings Bond Application - Dockerfile
# Multi-service container for Streamlit applications

FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (minimal set)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code with proper ownership
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default port (can be overridden via docker-compose or --build-arg)
ARG PORT=8501
ENV PORT=${PORT}
EXPOSE ${PORT}

# Health check - Streamlit exposes /_stcore/health
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl --fail http://localhost:${PORT}/_stcore/health || exit 1

# Default command (overridden in docker-compose for admin app)
CMD ["sh", "-c", "streamlit run src/streamlit_app.py --server.port=${PORT} --server.address=0.0.0.0"]
