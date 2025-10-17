# Stage 1 — build dependencies
FROM python:3.11-slim AS builder
WORKDIR /app
COPY app/requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && pip install --upgrade pip \
    && pip wheel --wheel-dir=/wheels -r requirements.txt \
    && apt-get purge -y --auto-remove build-essential

# Stage 2 — final lightweight runtime
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 PYTHONHASHSEED=0
WORKDIR /app

# copy wheels and install deps
COPY --from=builder /wheels /wheels
COPY app/requirements.txt .
RUN pip install --no-index --find-links=/wheels -r requirements.txt

# copy source code and model
COPY app/ ./app/

# expose port
EXPOSE 8000

# healthcheck
HEALTHCHECK --interval=10s --timeout=2s CMD curl -f http://localhost:8000/health || exit 1

# start the API
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]