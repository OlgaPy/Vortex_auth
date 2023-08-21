from flask import Blueprint

from .auth import router as auth_router
from .users import router as users_router

api_routes = Blueprint("api", "api", url_prefix="/api")
api_routes.register_blueprint(users_router)
api_routes.register_blueprint(auth_router)
