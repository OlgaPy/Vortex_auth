FROM python:3.11-slim-buster AS prod
COPY requirements/base.txt /tmp/base.txt
RUN pip install -r /tmp/base.txt
WORKDIR /app
COPY ./app .
CMD ["uvicorn", "app.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "3333"]

FROM prod AS dev
COPY requirements/dev.txt /tmp/dev.txt
RUN pip install -r /tmp/dev.txt && \
    apt update && apt install git gcc -y
ENV PYTHONPATH /
CMD ["uvicorn", "app.main:app", "--reload", "--proxy-headers", "--host", "0.0.0.0", "--port", "3333"]
