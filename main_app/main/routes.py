from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_required, login_user
from flask_misaka import markdown
from . import bp
from main_app import db
from main_app.models import Users
from main_app.log import logger


@bp.route("/about")
@login_required
def aboutPage():
    readme_file = open("README.md", "r")
    read_me_html = markdown(readme_file.read(), fenced_code=True)
    return render_template(
        "about.html",
        read_me_html=read_me_html,
        title="About",
    )


# @bp.route("/testing")
# @login_required
# def displayTest():
#     return render_template("test.html", title="Test")