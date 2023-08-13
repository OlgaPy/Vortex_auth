import os

import flask

from models.errors import AppException, UnknownError
from routes import api_routes
from injectors.connections import init_tables


app = flask.Flask(__name__)
app.register_blueprint(api_routes)

init_tables()


# @app.errorhandler(Exception)
# def error_handler(error: Exception):
#     if isinstance(error, AppException):
#         return error.to_dict(), error.http_code
#     else:
#         return UnknownError()


if __name__ == '__main__':
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", 80))
    app.run(host, port)
