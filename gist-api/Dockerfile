# Dockerfile
FROM python:3.12-slim

# Create a non-root user and group
ARG APP_USER=appuser
ARG APP_UID=1000
RUN groupadd -g ${APP_UID} ${APP_USER} \
    && useradd -m -u ${APP_UID} -g ${APP_UID} -s /bin/sh ${APP_USER}

WORKDIR /app

# Install build deps (minimal), then runtime deps
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt /app/requirements.txt
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libffi-dev build-essential \
    && pip install --no-cache-dir -r /app/requirements.txt \
    && apt-get remove -y gcc build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Copy application
COPY app /app/app
COPY tests /app/tests

# Ensure files owned by non-root user
RUN chown -R ${APP_USER}:${APP_USER} /app

USER ${APP_USER}

EXPOSE 8080

# Run uvicorn on port 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]