# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install necessary system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Upgrade pip
RUN pip install --upgrade pip

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code into the container
COPY . .

# Expose port 8000 for the FastAPI application
EXPOSE 8000

# Command to run multiple Uvicorn workers for concurrency
CMD ["uvicorn", "api.lead_generation_api:create_app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"] 
