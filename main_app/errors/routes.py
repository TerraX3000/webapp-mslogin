from flask import render_template
from . import bp
from main_app.log import logger, wrap, entering, exiting

# Reference: Python Flask Tutorials: Tutorial 12: Custom Error Pages
# https://coreyms.com/development/python/python-flask-tutorials-full-series


@bp.app_errorhandler(404)
@wrap(entering, exiting)
def error_404(error):
    return render_template("404.html", title="404 Error"), 404


@bp.app_errorhandler(401)
@wrap(entering, exiting)
def error_401(error):
    return render_template("401.html", title="401 Error"), 401


@bp.app_errorhandler(403)
@wrap(entering, exiting)
def error_403(error):
    return render_template("403.html", title="403 Error"), 403


@bp.app_errorhandler(500)
@wrap(entering, exiting)
def error_500(error):
    return render_template("500.html", title="500 Error"), 500
