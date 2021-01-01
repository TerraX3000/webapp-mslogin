from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_required, login_user
from . import bp
from main_app import db
from main_app.models import Users
from main_app.log import logger


@bp.route("/about")
@login_required
def aboutPage():
    return render_template("about.html", title="About")
