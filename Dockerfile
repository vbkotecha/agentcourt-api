FROM python:3.12-slim AS base

LABEL org.opencontainers.image.title="AgentCourt" \
      org.opencontainers.image.description="Policy-driven dispute resolution API for AI agent commerce" \
      org.opencontainers.image.source="https://github.com/vbkotecha/agentcourt-api" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.version="1.3.0"

WORKDIR /app

# Install only what we need
RUN pip install --no-cache-dir fastapi uvicorn[standard] pydantic

# Copy source
COPY src/ ./src/
COPY sdk/ ./sdk/
COPY tests/ ./tests/

# Run as non-root user
RUN useradd -m -u 1000 agentcourt && chown -R agentcourt:agentcourt /app
USER agentcourt

# Expose port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT:-8000}/health').read()" || exit 1

# Run — Railway provides $PORT
CMD ["sh", "-c", "python3 -m uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
