FROM python:3.12-slim

WORKDIR /app

# Install only what we need
RUN pip install --no-cache-dir fastapi uvicorn[standard] pydantic

# Copy source
COPY src/ ./src/
COPY sdk/ ./sdk/
COPY tests/ ./tests/

# Expose port
EXPOSE 8000

# Run — Railway provides $PORT
CMD ["sh", "-c", "python3 -m uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
