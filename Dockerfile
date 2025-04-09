FROM python:3.10-alpine

RUN apk update && apk upgrade --no-cache
RUN apk --no-cache -q add git build-base linux-headers tzdata
ENV TZ=Asia/Kolkata
RUN pip install --no-cache-dir -U pip

WORKDIR /app
COPY requirements.txt /app
RUN pip install -U -r requirements.txt

COPY . /app

CMD ["python3", "main.py"]