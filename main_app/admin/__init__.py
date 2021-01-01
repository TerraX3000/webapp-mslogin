from flask import Blueprint

bp = Blueprint(
    "admin", __name__, template_folder="../templates/admin", static_folder="static"
)
