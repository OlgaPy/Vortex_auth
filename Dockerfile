FROM python:3.11-slim-buster

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt && \
    apt update && apt install git gcc -y && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY ./app .

ENV PYTHONPATH /

CMD ["uvicorn", "app.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "3333"]
