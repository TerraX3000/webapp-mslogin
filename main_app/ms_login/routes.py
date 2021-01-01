from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
    session,
    current_app,
    abort,
)

from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
)

from . import bp

import requests

import uuid
import msal
from main_app.config_msa import Config as app_config
from main_app import _build_auth_url, _build_msal_app
from main_app.log import logger, wrap, entering, exiting
from main_app.models import Users
from main_app.main.referenceData import getUserRoles, getStringListOfUserRoles


@bp.route("/")
def index():
    if not session.get("user"):
        return redirect(url_for("ms_login.login"))
    return render_template("index.html", user=session["user"], title="Home")


@bp.route("/login")
def login():
    session["state"] = str(uuid.uuid4())
    # Technically we could use empty list [] as scopes to do just sign in,
    # here we choose to also collect end user consent upfront
    auth_url = _build_auth_url(scopes=app_config.SCOPE, state=session["state"])
    return render_template("login.html", auth_url=auth_url, title="Login")


@bp.route("/userprofile")
@login_required
def userprofile():
    users_email = session["user"]["preferred_username"]
    logger.info("users_email = %s", users_email)
    user = Users.query.filter(Users.email == users_email).first()
    stringListOfRoles = getStringListOfUserRoles(user)
    return render_template(
        "userprofile.html", user=user, userRoles=stringListOfRoles, title="User Profile"
    )


@bp.route(
    app_config.REDIRECT_PATH
)  # Its absolute URL must match your app's redirect_uri set in AAD
def authorized():
    if request.args.get("state") != session.get("state"):
        return redirect(url_for("ms_login.index"))  # No-OP. Goes back to Index page
    if "error" in request.args:  # Authentication/Authorization failure
        return render_template("auth_error.html", result=request.args, title="Error")
    if request.args.get("code"):
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_authorization_code(
            request.args["code"],
            scopes=app_config.SCOPE,  # Misspelled scope would cause an HTTP 400 error here
            redirect_uri=url_for("ms_login.authorized", _external=True),
        )
        if "error" in result:
            return render_template("auth_error.html", result=result, title="Error")
        print(loginApprovedUser(result.get("id_token_claims")))
        flash("User logged in!", "success")
        _save_cache(cache)
    return redirect(url_for("ms_login.index"))


@bp.route("/logout")
def logout():
    session.clear()  # Wipe out user and its token cache from session
    return redirect(  # Also logout from your tenant's web session
        app_config.AUTHORITY
        + "/oauth2/v2.0/logout"
        + "?post_logout_redirect_uri="
        + url_for("ms_login.index", _external=True)
    )


@bp.route("/graphcall")
@login_required
def graphcall():
    token = _get_token_from_cache(app_config.SCOPE)
    if not token:
        return redirect(url_for("ms_login.login"))
    graph_data = requests.get(  # Use token to call downstream service
        app_config.ENDPOINT,
        headers={"Authorization": "Bearer " + token["access_token"]},
    ).json()
    return render_template(
        "display.html", result=graph_data, title="Graph API Call Result"
    )


@wrap(entering, exiting)
@bp.route("/test")
def loginTest():
    """Provides method to sign into the app using a test account"""
    users_email = "test@test"
    logger.info("users_email = %s", users_email)
    user = Users.query.filter(Users.email == users_email).first()
    logger.info("User query result = %s", user)

    try:
        logger.info("Logged in with test account")
        user_info = {"name": "Test User", "preferred_username": users_email}
        # Begin user session by logging the user in
        login_user(user)
        session["user"] = user_info
        session["user"]["roles"] = getUserRoles(user)
        flash("You are logged in with the test account", "success")
    except:
        abort(401)

    return render_template("logintest.html", title="Test Login")


def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache


def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()


def _get_token_from_cache(scope=None):
    cache = _load_cache()  # This web app maintains one cache per session
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if accounts:  # So all account(s) belong to the current signed-in user
        result = cca.acquire_token_silent(scope, account=accounts[0])
        _save_cache(cache)
        return result


def loginApprovedUser(id_token_claims):
    # Verify user is approved to access the apps
    if "preferred_username" in id_token_claims:
        users_email = id_token_claims["preferred_username"]
        print("users_email=", users_email)
        user = Users.query.filter(Users.email == users_email).first()
        print("User query result =", user)
        print("User type =", type(user))

        if user:
            logger.info("This is a valid user")
            # Begin user session by logging the user in
            login_user(user)
            session["user"] = id_token_claims
            session["user"]["roles"] = getUserRoles(user)
            return True
        logger.info("This is not a valid user")
    return False