FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app/src:/app/src/agents:/app/src/core:/app/src/a2a"

WORKDIR /app

# System deps (optional: curl for healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Install dependencies first (leveraging build cache)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy source
COPY . /app

WORKDIR /app

# Default command can be overridden in docker-compose per service
CMD ["python", "src/a2a/a2a_integration.py"]


