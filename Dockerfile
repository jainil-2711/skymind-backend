# Use official Python 3.11 slim image — smaller than full Python image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Set environment variables
# Prevents Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout/stderr — logs appear immediately
ENV PYTHONUNBUFFERED=1

# Install system dependencies needed by psycopg2
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies first
# This layer is cached — Docker won't reinstall unless requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 8000
EXPOSE 8000

# Start the FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]