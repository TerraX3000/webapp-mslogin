from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from datetime import date, time

from . import bp
from main_app import db
from main_app.log import logger, wrap, entering, exiting

from main_app.models import Templates
from main_app.main.utilityFunctions import printLogEntry
from .forms import (
    submitNewTemplateForm,
    chooseTemplateToEditForm,
    editTemplateForm,
    testTemplateForm,
)
from .templateManager import (
    add_Template,
    update_Template,
    renderEmailTemplate,
    preview_Template,
    getTemplatesToEdit,
)


@bp.route("/templatemanager", methods=["GET", "POST"])
@login_required
def displayTemplates():
    # Handles creating, editing, and testing email templates
    printLogEntry("displayTemplates() function called")
    newTemplateFormDetails = submitNewTemplateForm()

    # Populate the selection form with the existing templates to choose edit
    chooseTemplateToEdit = chooseTemplateToEditForm()
    chooseTemplateToEdit.templateTitle.choices = getTemplatesToEdit()

    editTemplateFormDetails = editTemplateForm()

    testTemplateFormDetails = testTemplateForm()
    # Initialize jinja2 templates to prevent potential errors
    jinja2Rendered_emailSubject = None
    jinja2Rendered_templateContent = None
    # Get all of the templates stored in the database
    templatesFromDB = (
        db.session.query(
            Templates.templateTitle,
        )
        .order_by(
            Templates.templateTitle,
        )
        .all()
    )
    # Process form information to create a new template
    if "submitNewTemplate" in request.form:
        if newTemplateFormDetails.validate_on_submit():
            printLogEntry("New Template Submitted")
            # print("templateFormDetails=", request.form)
            add_Template(
                newTemplateFormDetails.templateTitle.data,
                newTemplateFormDetails.emailSubject.data,
                newTemplateFormDetails.templateContent.data,
            )
            db.session.commit()
            flash("New template has been added!", "success")
            return redirect(url_for("templateManager.displayTemplates"))

    # Process form information to update existing template
    if "submitUpdatedTemplate" in request.form:
        if editTemplateFormDetails.validate_on_submit():
            printLogEntry("Updated Template Submitted")
            # print("editTemplateFormDetails=", request.form)
            update_Template(
                editTemplateFormDetails.template_id.data,
                editTemplateFormDetails.templateTitle.data,
                editTemplateFormDetails.emailSubject.data,
                editTemplateFormDetails.templateContent.data,
            )
            db.session.commit()
            flash("New template has been added!", "success")
            return redirect(url_for("templateManager.displayTemplates"))

    # Return the current template details of the form selected for editing
    if "chooseTemplateToEdit" in request.form:
        # print("chooseTemplateToEdit form", request.form)
        emailTemplate = Templates.query.filter(
            Templates.id == chooseTemplateToEdit.templateTitle.data
        ).first()
        if emailTemplate:
            editTemplateFormDetails.template_id.data = emailTemplate.id
            editTemplateFormDetails.templateTitle.data = emailTemplate.templateTitle
            editTemplateFormDetails.emailSubject.data = emailTemplate.emailSubject
            editTemplateFormDetails.templateContent.data = emailTemplate.templateContent
            (
                jinja2Rendered_emailSubject,
                jinja2Rendered_templateContent,
            ) = preview_Template(
                editTemplateFormDetails.emailSubject.data,
                editTemplateFormDetails.templateContent.data,
            )

            testTemplateFormDetails.emailSubject.data = emailTemplate.emailSubject
            testTemplateFormDetails.templateContent.data = emailTemplate.templateContent
        else:
            editTemplateFormDetails = None
    else:
        editTemplateFormDetails = None

    # Process form information to test template
    if "submitTestTemplate" in request.form:
        if testTemplateFormDetails.validate_on_submit():
            printLogEntry("Test Template Submitted")
            # print("templateFormDetails=", request.form)
            (
                jinja2Rendered_emailSubject,
                jinja2Rendered_templateContent,
            ) = preview_Template(
                testTemplateFormDetails.emailSubject.data,
                testTemplateFormDetails.templateContent.data,
            )

    return render_template(
        "templatemanager.html",
        title="Template Manager",
        templates=templatesFromDB,
        templateForm=newTemplateFormDetails,
        chooseTemplateToEdit=chooseTemplateToEdit,
        editTemplateForm=editTemplateFormDetails,
        testTemplateForm=testTemplateFormDetails,
        rendered_emailSubject=jinja2Rendered_emailSubject,
        rendered_templateContent=jinja2Rendered_templateContent,
    )


@bp.route("/templatemanager/<int:log_id>/delete", methods=["POST"])
@login_required
def delete_Template(log_id):
    # Handle deleting of existing templates
    log = Templates.query.get_or_404(log_id)
    LogDetails = f"{(log_id)} {log.templateTitle}"
    printLogEntry("Running delete_Template(" + LogDetails + ")")
    db.session.delete(log)
    db.session.commit()
    flash("Template has been deleted!", "success")
    return redirect(url_for("templateManager.displayTemplates"))
