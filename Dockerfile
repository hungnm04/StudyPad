# Multi-stage build for optimization
FROM python:3.12-alpine as builder

# Install build dependencies
RUN apk add --no-cache gcc musl-dev jpeg-dev zlib-dev freetype-dev

# Build Python wheels
COPY noteApp/requirements.txt /tmp/
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r /tmp/requirements.txt

# Final stage - runtime image
FROM python:3.12-alpine

WORKDIR /app

# Install runtime dependencies and create user named 'app' (matches workdir)
RUN apk add --no-cache jpeg zlib freetype curl && \
    adduser -D -u 1000 app

# Install Python packages from wheels
COPY --from=builder /app/wheels /wheels
COPY noteApp/requirements.txt .
RUN pip install --no-cache /wheels/* && rm -rf /wheels

# Copy application code with proper ownership to 'app' user
COPY --chown=app:app ./noteApp .

# Create directories, collect static files, and set permissions (as root)
RUN mkdir -p static media/uploads && \
    python manage.py collectstatic --noinput && \
    chown -R app:app static media

# Switch to 'app' user (non-root)
USER app
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]