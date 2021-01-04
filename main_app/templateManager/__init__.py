from flask import Blueprint

bp = Blueprint(
    "templateManager", __name__, template_folder="../templates/templateManager"
)
