# Use python 3.11 (matches your project version)
FROM python:3.11-slim

# Set working directory to the root of the container
WORKDIR /app

# Prevent Python from writing .pyc files and buffer stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies (needed for psycopg2 and other build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from the project root
COPY requirements.txt .

# Install Python dependencies with a higher timeout to prevent network errors
# Added: --default-timeout=100
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt

# Copy the app code
COPY app/ ./app/

# Expose the port FastAPI runs on
EXPOSE 8000

# Start the server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
