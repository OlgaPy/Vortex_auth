FROM python:3.11-slim-buster

ARG BUILD_DEPENDENCES=gcc

ADD requirements.txt /tmp/requirements.txt
RUN set -e; \
    apt update; \
    apt install -y ${BUILD_DEPENDENCES}; \
    pip install -r /tmp/requirements.txt; \
    apt purge --autoremove -y ${BUILD_DEPENDENCES}; \
    rm -rf /var/lib/apt/lists/*;

ADD . /app
WORKDIR /app/src

CMD ["uwsgi", "--ini", "../uwsgi.ini"]