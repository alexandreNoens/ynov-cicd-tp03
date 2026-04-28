FROM python:3.12-alpine3.23 AS build

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

RUN python -m venv "$VIRTUAL_ENV"

COPY requirements/requirements.lock .
RUN pip install --no-cache-dir -r requirements.lock \
 && rm requirements.lock \
 && find /opt/venv -type d -name "__pycache__" -exec rm -rf {} + \
 && find /opt/venv -type f -name "*.pyc" -delete

FROM python:3.12-alpine3.23 AS production

LABEL maintainer="alexandre"
LABEL version="1.0.0"

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

RUN addgroup -S app && adduser -S -G app -h /home/app app

COPY --from=build /opt/venv /opt/venv
COPY app ./app
COPY sql ./sql

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
	CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2).read()"

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
