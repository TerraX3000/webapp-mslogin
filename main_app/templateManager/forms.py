from flask_wtf import FlaskForm
from wtforms import (
    SubmitField,
    StringField,
    SelectField,
    TextAreaField,
    BooleanField,
    HiddenField,
)
from wtforms.validators import DataRequired, Optional


class submitNewTemplateForm(FlaskForm):
    templateTitle = StringField("Template Title")
    emailSubject = StringField("Email Subject")
    templateContent = TextAreaField("Template Content", render_kw={"rows": "20"})
    submitNewTemplate = SubmitField("Submit New Template")


class chooseTemplateToEditForm(FlaskForm):
    templateTitle = SelectField("Template Title")
    chooseTemplateToEdit = SubmitField("Choose Template to Edit")


class editTemplateForm(FlaskForm):
    template_id = HiddenField()
    templateTitle = StringField("Template Title")
    emailSubject = StringField("Email Subject")
    templateContent = TextAreaField("Template Content", render_kw={"rows": "20"})
    submitUpdatedTemplate = SubmitField("Submit Updated Template")


class testTemplateForm(FlaskForm):
    emailSubject = StringField("Test Email Subject")
    templateContent = TextAreaField("Test Template Content", render_kw={"rows": "20"})
    submitTestTemplate = SubmitField("Test Template")
