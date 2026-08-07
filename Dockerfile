FROM python:3.12-slim

WORKDIR /app

# Install system dependencies if required (e.g., for psycopg2 or geoalchemy2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./backend_requirements.txt
RUN pip install --no-cache-dir -r backend_requirements.txt

# Copy the ai-engine directory
COPY ai-engine ./ai-engine

# Copy the backend directory
COPY backend ./backend

# We need to set PYTHONPATH so that backend can run properly
ENV PYTHONPATH=/app/backend

# Cloud Run sets the PORT environment variable
ENV PORT=8080
EXPOSE 8080

# Run the backend using uvicorn
# We run from the /app/backend directory so uvicorn finds app.main
WORKDIR /app/backend
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
