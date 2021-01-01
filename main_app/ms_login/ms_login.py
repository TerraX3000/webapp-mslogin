from functools import wraps
from flask import url_for, request, redirect, session, flash
from main_app.main.referenceData import findUserByEmail, getUserRoles


def checkForAccess(user, access_roles):
    """Checks whether user has required access
    access_roles can be specified as a single item, list, or combination:

    # Ensures that the user is ('Starving' AND (an 'Artist' OR a 'Programmer'))
    @requires_access_level('Starving', ['Artist', 'Programmer'])
    """
    # Logic:
    # Set access_approved=True
    # Evaluate access tests for each access
    # Set access_approved=False if an access test fails
    # Return access_approved

    access_approved = True
    for access in access_roles:
        # Access Test 1: Test for required accesses
        if isinstance(access, str):
            if access not in getUserRoles(user):
                access_approved = False

        # Access Test 2: Test for at least one required access in list of accesses
        if isinstance(access, list):
            or_access_approved = False
            for access_item in access:
                if access_item in getUserRoles(user):
                    or_access_approved = True
            access_approved = all([access_approved, or_access_approved])
    return access_approved


def requires_access_level(*access_role):
    """The @requires_access_level decorator accepts one or more access_role names.
    At the decorator level, if multiple role names are specified here, the user must
    have all the specified roles. This is the AND operation.

    At the argument level, each item may be a role name or a list or role names.
    If a list of role names is specified here, the user mast have any one of the
    specified roles to gain access. This is the OR operation.

    In the example below, the user must always have the 'Starving' role, AND either
    the 'Artist' role OR the 'Programmer' role:

    # Ensures that the user is ('Starving' AND (an 'Artist' OR a 'Programmer'))
    @requires_access_level('Starving', ['Artist', 'Programmer'])
    Note: The nesting level only goes as deep as this example shows.

    This approach is modeled after the implementation used in Flask-User as described here:
    https://flask-user.readthedocs.io/en/latest/authorization.html
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Verify user is logged in and has required access role
            if not session.get("user"):
                return redirect(url_for("ms_login.login"))
            user = findUserByEmail(session["user"]["preferred_username"])
            if not checkForAccess(user, access_role):
                flash("You do not have access to that page. Sorry!", "error")
                return redirect(url_for("ms_login.index"))
            return f(*args, **kwargs)

        return decorated_function

    return decorator
