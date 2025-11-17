FROM python:3.11-slim AS build-env

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --disable-pip-version-check --no-cache-dir \
        -r requirements.txt --target /packages

FROM gcr.io/distroless/python3-debian12

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/packages

WORKDIR /app

COPY app.py /app/app.py
COPY --from=build-env /packages /packages

EXPOSE 8080

CMD ["-m", "gunicorn", "-b", "0.0.0.0:8080", "app:app"]