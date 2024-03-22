FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt update && apt install -y python3-pip python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0

RUN pip install "poetry==1.7.1" && poetry config virtualenvs.create false --local

COPY pyproject.toml poetry.lock ./

RUN poetry update

RUN poetry install --no-root

COPY src .
