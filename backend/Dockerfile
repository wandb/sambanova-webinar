# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

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

# Command to run the backend service
CMD ["uvicorn", "api.lead_generation_api:app", "--host", "0.0.0.0", "--port", "8000"] 