from flask import flash, current_app, send_file, Markup
from jinja2 import Template
from flask_misaka import markdown
from main_app import db
from main_app.models import Templates
from main_app.main.utilityFunctions import printLogEntry
from datetime import date, time


def add_Template(
    templateTitle,
    emailSubject,
    templateContent,
):
    # Add new template to the database
    printLogEntry("add_Template() function called")
    print(templateTitle)
    newTemplate = Templates(
        templateTitle=templateTitle,
        emailSubject=emailSubject,
        templateContent=templateContent,
    )
    db.session.add(newTemplate)
    return


def update_Template(
    template_id,
    templateTitle,
    emailSubject,
    templateContent,
):
    # Update information for existing template
    printLogEntry("update_Template() function called")
    templateFromDB = Templates.query.get(template_id)
    print(templateTitle)
    templateFromDB.templateTitle = templateTitle
    templateFromDB.emailSubject = emailSubject
    templateFromDB.templateContent = templateContent
    return


def renderEmailTemplate(emailSubject, templateContent, templateParams):
    # Try to render the template but provide a nice message if it fails to render
    # Important to keep these try/except cases since users can easily create
    # mistakes when creating email templates.  Without these try/except cases,
    # users would be unable to fix the mistakes.
    # Improve: provide the error details in the exception message so they user
    # can identify the error
    # print(emailSubject, templateContent, templateParams)
    try:
        jinja2Template_emailSubject = Template(emailSubject)
        jinja2Rendered_emailSubject = jinja2Template_emailSubject.render(templateParams)
    except:
        jinja2Rendered_emailSubject = (
            "Rendering error.  Fix your template and try again."
        )
    try:

        jinja2Template_templateContent = Template(templateContent)
        jinja2Rendered_templateContent = jinja2Template_templateContent.render(
            templateParams
        )
        jinja2Rendered_templateContent = jinja2Rendered_templateContent
        # jinja2Rendered_templateContent = markdown(
        #     jinja2Rendered_templateContent, hard_wrap=True
        # )
    except:
        jinja2Rendered_templateContent = (
            "Rendering error.  Fix your template and try again."
        )
    # Uncomment these print statements if debugging rendering issues
    # print("jinja2Rendered_emailSubject =", jinja2Rendered_emailSubject)
    # print("jinja2Rendered_templateContent =", jinja2Rendered_templateContent)
    return jinja2Rendered_emailSubject, jinja2Rendered_templateContent


def preview_Template(emailSubject, templateContent):
    # Sample template variables
    # Create templateParams dictionary used for rendering templates
    templateParams = {
        "firstName": "Smarty",
        "lastName": "Tester",
        "orgName": "Acme, Inc.",
        "startDate": date(2021, 1, 11),
        "endDate": date(2021, 1, 12),
        "startTime": time(11, 0),
        "endTime": time(12, 0),
        "eventNumber": 42,
        "comment": "random comment for testing",
        "webLink": "http://google.com/",
        "simpleList": ["Smarty Tester", "Testy Tester", "Betty Tester"],
        "eventList": [
            {
                "eventName": "Event Alpha",
                "eventDate": date(2021, 1, 11),
                "startTime": time(10, 0),
                "endTime": time(11, 0),
            },
            {
                "eventName": "Event Bravo",
                "eventDate": date(2021, 1, 13),
                "startTime": time(11, 0),
                "endTime": time(12, 0),
            },
            {
                "eventName": "Event Charlie",
                "eventDate": date(2021, 1, 15),
                "startTime": time(13, 0),
                "endTime": time(14, 0),
            },
        ],
    }
    # Important: Rendering for previewing is done in this sequence:
    # 1. Call renderEmailTemplate to render Jinja template variables
    # 2. Markup rendered template to convert Jinja Template object to HTML
    # 3. Markup HTML template with markdown to convert markdown to HTML
    jinja2Rendered_emailSubject, jinja2Rendered_templateContent = renderEmailTemplate(
        emailSubject, templateContent, templateParams
    )
    # print(jinja2Rendered_templateContent)
    # jinja2Rendered_templateContent = Markup(jinja2Rendered_templateContent)
    # print(jinja2Rendered_templateContent)
    jinja2Rendered_templateContent = markdown(
        jinja2Rendered_templateContent, hard_wrap=True
    )
    # print(jinja2Rendered_templateContent)
    flash("Test template rendered!", "success")
    return jinja2Rendered_emailSubject, jinja2Rendered_templateContent


def getTemplatesToEdit():
    templatesValueLabelTupleList = (
        db.session.query(Templates.id, Templates.templateTitle)
        .order_by(
            Templates.templateTitle,
        )
        .all()
    )
    templatesValueLabelTupleList.insert(0, ("", ""))
    return templatesValueLabelTupleList