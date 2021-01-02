from main_app import db
from main_app.models import Users, UserRoles, Role, adminSettings


def getUsers():
    """Get list of user to display as dropdown choices but exclude system account"""
    userTupleList = (
        db.session.query(Users.id, Users.firstName, Users.lastName)
        .filter(Users.lastName != "System")
        .distinct()
        .order_by(Users.lastName)
        .all()
    )
    userValueLabelTupleList = [
        (item[0], item[1] + " " + item[2]) for item in userTupleList
    ]
    return userValueLabelTupleList


def findUserByEmail(user_email):
    """Return the user associated with this email"""
    user = db.session.query(Users).filter(Users.email == user_email).first()
    return user


def getUserRoles(user):
    """Returns list of roles for the user"""
    userRoleTupleList = (
        db.session.query(
            Role.name,
        )
        .select_from(Users)
        .join(UserRoles)
        .join(Role)
        .filter(Users.id == user.id)
        .all()
    )
    roles = []
    for role in userRoleTupleList:
        roles.append(role[0])
    return roles


def getStringListOfUserRoles(user):
    """Returns comma-separated string of roles for the user"""
    listOfRoles = getUserRoles(user)
    stringListOfRoles = ", ".join(listOfRoles)
    return stringListOfRoles


def getRoleChoices():
    """Get list of roles to display as dropdown choices"""
    roleTupleList = db.session.query(Role.id, Role.name).order_by(Role.id).all()
    return roleTupleList


def getSystemAccountEmail():
    """Get email address for the system account"""
    systemAccountEmail = (
        db.session.query(Users.email).filter(Users.lastName == "System").first()
    )
    return systemAccountEmail[0]


def setSystemModeStatus(systemModeStatus):
    """ Set system mode status to enableLiveMode=True or enableLiveMode=False"""
    newAdminSettings = adminSettings(enableOpsMode=systemModeStatus)
    db.session.add(newAdminSettings)
    return


def getSystemModeStatus():
    """Get current system mode"""
    systemModeStatus = (
        db.session.query(adminSettings.enableOpsMode)
        .order_by(adminSettings.id.desc())
        .first()
    )
    return systemModeStatus[0]