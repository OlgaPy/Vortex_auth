import os

import flask
from models.errors import AppException, UnknownError

app = flask.Flask(__name__)


@app.errorhandler(Exception)
def error_handler(error: Exception):
    if isinstance(error, AppException):
        return error.to_dict(), error.http_code
    else:
        return UnknownError()


@app.get("/")
def main():
    return "Ok", 200


if __name__ == '__main__':
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", 80))
    app.run(host, port)
