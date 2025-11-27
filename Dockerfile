# Multi-stage build for minimal image size
FROM python:3.13-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml uv.lock ./
COPY src/email_signature/__version__.py ./src/email_signature/__version__.py

# Install uv and dependencies
RUN pip install --no-cache-dir uv && \
    uv pip install --system --no-cache .

# Runtime stage
FROM python:3.13-slim

WORKDIR /app

# Install runtime dependencies (fonts for signature generation)
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages

# Copy application code
COPY src/ ./src/
COPY main.py ./
COPY config/ ./config/
COPY logo.png ./

# Create directories for volumes
RUN mkdir -p /app/output /app/profiles /app/config

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV OUTPUT_DIR=/app/output

# Run as non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Default command runs the CLI interface
ENTRYPOINT ["python", "main.py"]
