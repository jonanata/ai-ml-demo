# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set workdir
WORKDIR /app

# Copy only requirements first for better caching
COPY requirements.txt ./

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . /app

# Expose port
EXPOSE 8000

# Use gunicorn with uvicorn workers in production
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
