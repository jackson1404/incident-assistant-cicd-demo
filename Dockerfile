FROM python:3.12-slim

RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN useradd \
    --system \
    --uid 10001 \
    --create-home \
    appuser

COPY requirements.txt .

# Install and validate application dependencies.
# Remove unnecessary build/package-management tools afterward.
RUN python -m pip install \
        --no-cache-dir \
        -r requirements.txt \
    && python -m pip check \
    && python -m pip uninstall -y setuptools \
    && python -m pip uninstall -y pip

COPY --chown=appuser:appuser app ./app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s \
    --timeout=5s \
    --start-period=10s \
    --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]