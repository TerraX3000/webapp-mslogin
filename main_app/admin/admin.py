from flask import flash, current_app, send_file
from main_app import db
from main_app.models import Users, Role, UserRoles
from datetime import datetime, date, time
from main_app.log import logger, wrap, entering, exiting
import csv
import os


# ###################
#    User Info     #
# ###################

# Add userto database
@wrap(entering, exiting)
def addUserToDatabase(firstName, lastName, position, email):
    """Adds new user to the database"""
    # Only add the user if the email is not already in the database
    if len(Users.query.filter_by(email=email).all()) == 0:
        user = Users(
            firstName=firstName,
            lastName=lastName,
            position=position,
            email=email,
        )
        logger.info(user)
        db.session.add(user)
        db.session.commit()
        flash("User has been added!", "success")
    else:
        logger.info("User with email %s already exists", email)
        flash(f"User with email {email} already exists", "error")
    return user


def addUserRoleToDatabase(user, role):
    user_roles = UserRoles(user_id=user.id, role_id=int(role))
    db.session.add(user_roles)
    db.session.commit()


@wrap(entering, exiting)
def downloadUserList():
    """Create a CSV output file and append with a timestamp"""
    output_file_path = os.path.join(current_app.root_path, "static/download")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file_path = "/tmp"
    csvFilename = output_file_path + "/" + "user_list_" + timestamp + ".csv"
    csvOutputFile = open(csvFilename, "w")
    csvOutputWriter = csv.writer(
        csvOutputFile, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
    )
    # Write header row for CSV file
    csvOutputWriter.writerow(
        [
            "firstName",
            "lastName",
            "position",
            "email",
        ]
    )
    csvOutputFileRowCount = 0
    # Query Student for student information
    users = Users.query.order_by(Users.lastName)
    # Process each record in the query and write to the output file
    for user in users:
        firstName = user.firstName
        lastName = user.lastName
        position = user.position
        email = user.email

        csvOutputWriter.writerow(
            [
                firstName,
                lastName,
                position,
                email,
            ]
        )
        csvOutputFileRowCount = csvOutputFileRowCount + 1
    csvOutputFile.close()
    return send_file(csvFilename, as_attachment=True, cache_timeout=0)


@wrap(entering, exiting)
def uploadUserList(fname):
    csvFile = open(fname, "r")
    importCSV = csv.reader(csvFile)
    for row in importCSV:
        # Skip the first row if it has header row data
        if "firstName" in row:
            continue
        logger.debug("row= %s", row)
        firstName = row[0].strip()
        lastName = row[1].strip()
        position = row[2].strip()
        email = row[3].strip()
        addUserToDatabase(
            firstName,
            lastName,
            position,
            email,
        )
    return


@wrap(entering, exiting)
def deleteUser(log_id):
    user = Users.query.filter_by(id=log_id).first()
    firstName = user.firstName
    lastName = user.lastName
    db.session.delete(user)
    db.session.commit()
    logger.info("User deleted from database: %s %s" % (firstName, lastName))
    flash("User has been deleted!", "success")
    return