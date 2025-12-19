FROM python:3.11-slim

# --- system deps ---
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# --- workdir ---
WORKDIR /app

# --- install deps ---
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- copy app ---
COPY app ./app

# --- env ---
ENV PYTHONUNBUFFERED=1

# --- run ---
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
