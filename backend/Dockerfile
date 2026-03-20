FROM python:3.12-slim

WORKDIR /app

# Install system dependencies including curl for health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (bind mount will override in dev)
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Command is overridden by docker-compose with --reload flag
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
