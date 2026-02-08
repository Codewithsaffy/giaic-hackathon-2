# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements (relative to build context root)
COPY src/notification_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user
RUN addgroup --system --gid 1001 appuser && \
    adduser --system --uid 1001 --gid 1001 appuser

# Copy shared and service code
COPY src /app/src

# Adjust permissions
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 80

CMD ["uvicorn", "src.notification_service.main:app", "--host", "0.0.0.0", "--port", "80"]
