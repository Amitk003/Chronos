FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    fastapi>=0.115.0 \
    "uvicorn[standard]>=0.34.0" \
    pydantic>=2.0.0 \
    httpx>=0.28.0 \
    apscheduler>=3.10.0 \
    sqlalchemy>=2.0.0 \
    cryptography>=42.0.0 \
    pydantic-settings>=2.0.0

COPY . .

EXPOSE 7860

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860}
