from flask import render_template, redirect, url_for, flash, request, abort, session
from flask_login import login_required
from main_app import db
from . import bp
from .forms import (
    addUserForm,
    selectUserToEditForm,
    downloadUserListForm,
    updateUserForm,
    uploadUserListForm,
    deleteUserForm,
)

from .admin import (
    addUserToDatabase,
    addUserRoleToDatabase,
    downloadUserList,
    uploadUserList,
    deleteUser,
)

from main_app.models import Users, UserRoles

from main_app.main.referenceData import (
    getUsers,
    setSystemModeStatus,
    getSystemModeStatus,
    getRoleChoices,
    getUserRoles,
    getStringListOfUserRoles,
)

from main_app.main.utilityFunctions import (
    printFormErrors,
    send_file,
    save_File,
)
from main_app.log import logger, wrap, entering, exiting
from main_app.ms_login.ms_login import requires_access_level


@bp.route("/templates/user_list_template")
@login_required
def downloadUserListTemplate():
    try:
        return send_file(
            "static/templates/user_list_template.csv",
            attachment_filename="user_list_template.csv",
            as_attachment=True,
            cache_timeout=0,
        )
    except Exception as e:
        logger.error("Unable to download user_list_template " + str(e))
        return str(e)


@wrap(entering, exiting)
@bp.route("/admin", methods=["GET", "POST"])
@requires_access_level("Admin")
def displayAdmin():
    addUserFormDetails = addUserForm()
    addUserFormDetails.role.choices = getRoleChoices()
    selectUserToEditFormDetails = selectUserToEditForm()
    selectUserToEditFormDetails.userName.choices = getUsers()
    downloadUserListFormDetails = downloadUserListForm()
    uploadUserListFormDetails = uploadUserListForm()
    deleteUserFormDetails = deleteUserForm()
    deleteUserFormDetails.userName.choices = getUsers()

    # Retrieve user info for display (except for system account)
    userInfo = Users.query.filter(Users.lastName != "System").order_by(
        Users.lastName.asc()
    )
    userRoleInfo = []
    for user in userInfo:
        userRoleInfo.append(getStringListOfUserRoles(user))

    # Retrieve current system mode
    SystemMode = getSystemModeStatus()
    # SystemMode = True

    if "submitAddUser" in request.form:
        if addUserFormDetails.validate_on_submit():
            logger.info("Add User submitted")
            firstName = addUserFormDetails.firstName.data
            lastName = addUserFormDetails.lastName.data
            position = addUserFormDetails.position.data
            email = addUserFormDetails.email.data
            role = addUserFormDetails.role.data

            user = addUserToDatabase(
                firstName,
                lastName,
                position,
                email,
            )
            addUserRoleToDatabase(user, role)
            return redirect(url_for("admin.displayAdmin"))
    printFormErrors(addUserFormDetails)

    if "submitDownloadUserListForm" in request.form:
        if downloadUserListFormDetails.validate_on_submit():
            logger.info("Download User List Form Submitted")
            return downloadUserList()

    if "submitUserToEdit" in request.form:
        if selectUserToEditFormDetails.validate_on_submit():
            logger.info("User to Edit Form Submitted")
            user_id = int(selectUserToEditFormDetails.userName.data)
            logger.info("user_id = %d", user_id)
            return redirect(url_for("admin.updateUser", user_id=user_id))
    printFormErrors(selectUserToEditFormDetails)

    if "submitUploadUserList" in request.form:
        if uploadUserListFormDetails.validate_on_submit():
            logger.info("Upload User List Form Submitted")
            if uploadUserListFormDetails.csvUserListFile.data:
                uploadedUserListFile = save_File(
                    uploadUserListFormDetails.csvUserListFile.data,
                    "Uploaded_UserList_File.csv",
                )
                uploadUserList(uploadedUserListFile)
                return redirect(url_for("admin.displayAdmin"))
    printFormErrors(uploadUserListFormDetails)

    if "submitDeleteUser" in request.form:
        if deleteUserFormDetails.validate_on_submit():
            if deleteUserFormDetails.confirmDeleteUser.data == "DELETE":
                logger.info("Delete User Form Submitted")
                # username returns log id as its value
                log_id = int(deleteUserFormDetails.userName.data)
                logger.info("log_id = %d", log_id)
                deleteUser(log_id)
                deleteUserFormDetails.confirmDeleteUser.data = ""
                # deleteClassScheduleFormDetails.process()
                return redirect(url_for("admin.displayAdmin"))
            else:
                deleteUserFormDetails.confirmDeleteUser.data = ""
                logger.info("Type DELETE in the text box to confirm delete")
    printFormErrors(deleteUserFormDetails)

    return render_template(
        "admin.html",
        title="Admin",
        userInfo=userInfo,
        userRoleInfo=userRoleInfo,
        addUserForm=addUserFormDetails,
        selectUserToEditForm=selectUserToEditFormDetails,
        downloadUserListForm=downloadUserListFormDetails,
        uploadUserListForm=uploadUserListFormDetails,
        deleteUserForm=deleteUserFormDetails,
        SystemMode=SystemMode,
    )


@wrap(entering, exiting)
@bp.route("/admin/setsystemmode", methods=["POST"])
@login_required
def setSystemMode():
    if "Admin" not in session["user"]["roles"]:
        abort(401)
    logger.info("Running setSystemMode()")
    if request.method == "POST":
        if request.form["submit_button"] == "Set to Test Mode":
            setSystemModeStatus(False)
            db.session.commit()
            logger.info("Enable Ops Mode = %s", getSystemModeStatus())
        elif request.form["submit_button"] == "Set to Ops Mode":
            setSystemModeStatus(True)
            db.session.commit()
            logger.info("Enable Ops Mode = %s", getSystemModeStatus())
    return redirect(url_for("admin.displayAdmin"))


@wrap(entering, exiting)
@bp.route("/admin/<int:user_id>/userupdate", methods=["GET", "POST"])
@login_required
def updateUser(user_id):
    if "Admin" not in session["user"]["roles"]:
        abort(401)
    logger.info("Running updateUser()")
    user = Users.query.get_or_404(user_id)
    role = UserRoles.query.filter_by(user_id=user.id).first()
    updateUserFormDetails = updateUserForm()
    updateUserFormDetails.role.choices = getRoleChoices()
    if "submitUpdateUser" in request.form:
        if updateUserFormDetails.validate_on_submit():
            user.firstName = updateUserFormDetails.firstName.data
            user.lastName = updateUserFormDetails.lastName.data
            user.email = updateUserFormDetails.email.data
            user.position = updateUserFormDetails.position.data
            role.role_id = updateUserFormDetails.role.data
            db.session.commit()
            userUpdateString = user.firstName + " " + user.lastName
            logger.info("User info updated for %s", userUpdateString)
            flash("User info for " + userUpdateString + " updated!", "success")
            return redirect(url_for("admin.displayAdmin"))
    elif request.method == "GET":
        updateUserFormDetails.user_id.data = user.id
        updateUserFormDetails.firstName.data = user.firstName
        updateUserFormDetails.lastName.data = user.lastName
        updateUserFormDetails.position.data = user.position
        updateUserFormDetails.email.data = user.email
        updateUserFormDetails.role.data = role.role_id
    return render_template(
        "updateuser.html",
        title="Update User",
        updateUserForm=updateUserFormDetails,
    )