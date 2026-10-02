# ============================================================
# RetroDoc Django Backend
# ============================================================

FROM python:3.14-slim

# Prevent Python from creating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Ensure Python output appears immediately in Docker logs
ENV PYTHONUNBUFFERED=1

# Production Django settings
ENV DJANGO_SETTINGS_MODULE=config.settings.production

# Application directory
WORKDIR /app


# ============================================================
# System dependencies
# ============================================================

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*


# ============================================================
# Python dependencies
# ============================================================

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


# ============================================================
# Application source
# ============================================================

COPY . .


# ============================================================
# Gunicorn
# ============================================================

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]