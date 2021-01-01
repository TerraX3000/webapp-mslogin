from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import (
    SubmitField,
    StringField,
    SelectField,
    HiddenField,
    SelectMultipleField,
    widgets,
    RadioField,
)
from wtforms.fields.html5 import DateField, EmailField
from wtforms.validators import DataRequired, Optional


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """

    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


# #################
#   User Info    #
# #################


class addUserForm(FlaskForm):
    firstName = StringField("First Name", validators=[DataRequired()])
    lastName = StringField("Last Name", validators=[DataRequired()])
    position = StringField("Position", validators=[Optional()])
    email = EmailField("Email", validators=[DataRequired()])
    role = RadioField("Access", coerce=int, validators=[DataRequired()])
    submitAddUser = SubmitField("Add User")


class selectUserToEditForm(FlaskForm):
    userName = SelectField("User Name", validators=[DataRequired()])
    submitUserToEdit = SubmitField("Edit User")


class updateUserForm(FlaskForm):
    user_id = HiddenField()
    firstName = StringField("First Name", validators=[DataRequired()])
    lastName = StringField("Last Name", validators=[DataRequired()])
    position = StringField("Position", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    role = RadioField("Access", coerce=int, validators=[DataRequired()])
    submitUpdateUser = SubmitField("Update User Info")


class downloadUserListForm(FlaskForm):
    submitDownloadUserListForm = SubmitField("Download User List")


class uploadUserListForm(FlaskForm):
    csvUserListFile = FileField(
        "User List (*.csv format)",
        validators=[FileAllowed(["csv"]), FileRequired()],
    )
    submitUploadUserList = SubmitField("Upload User List")


class deleteUserForm(FlaskForm):
    userName = SelectField("User Name", coerce=int, validators=[DataRequired()])
    confirmDeleteUser = StringField(
        "Type DELETE to confirm", validators=[DataRequired()]
    )
    submitDeleteUser = SubmitField("Delete User")