FROM python:3.11-slim-buster

ARG user=kapibara

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt && \
    rm -rf /var/lib/apt/lists/* && \
    useradd -U $user

USER $user:$user

WORKDIR /app
COPY ./app ./

CMD ["uvicorn", "app.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "3333"]
