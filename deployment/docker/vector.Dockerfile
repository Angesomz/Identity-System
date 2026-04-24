FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libopenblas-dev \
    libomp-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Placeholder command
CMD ["python", "-m", "vector_cluster.service_runner"]
