FROM python:3.11-slim

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    git build-essential linux-headers-amd64 tzdata && \
    rm -rf /var/lib/apt/lists/*

# Set timezone (use Asia/Kolkata if needed)
ENV TZ=Asia/Dhaka

RUN pip install --no-cache-dir -U pip wheel==0.45.1

WORKDIR /app
COPY requirements.txt /app
RUN pip install -U -r requirements.txt

COPY . /app

CMD ["python3", "main.py"]
