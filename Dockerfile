FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install dj-database-url

# Copy project
COPY . .

# Create necessary directories and set permissions
RUN mkdir -p /app/staticfiles /app/media /app/logs \
    && touch /app/logs/repaysync.log /app/logs/security.log \
    && chmod -R 777 /app/logs \
    && find . -path "*/migrations" -type d -exec chmod -R 777 {} \;

# Make sure migration directories exist with proper permissions
RUN mkdir -p \
    /app/users/migrations \
    /app/customers/migrations \
    /app/loans/migrations \
    /app/interactions/migrations \
    /app/core/migrations \
    && touch \
    /app/users/migrations/__init__.py \
    /app/customers/migrations/__init__.py \
    /app/loans/migrations/__init__.py \
    /app/interactions/migrations/__init__.py \
    /app/core/migrations/__init__.py \
    && chmod -R 777 \
    /app/users/migrations \
    /app/customers/migrations \
    /app/loans/migrations \
    /app/interactions/migrations \
    /app/core/migrations

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
