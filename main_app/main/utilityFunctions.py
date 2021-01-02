import os
from flask import send_file, current_app
from datetime import datetime


def save_File(form_UploadedFileData, filename):
    """Save file to server"""
    # file_path = os.path.join(current_app.root_path, "static/upload", filename)
    file_path = "/tmp" + "/" + filename
    form_UploadedFileData.save(file_path)
    return file_path


def download_File(filename):
    """Download file to user's system"""
    # file_path = os.path.join(current_app.root_path, "static/uploadfiles", filename)
    file_path = "/tmp" + "/" + filename
    print("download_File function called with filename=", file_path)
    return send_file(file_path, as_attachment=True, cache_timeout=0)


def printLogEntry(logEntry):
    """Print statement with timestamp"""
    logtime = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]  ")
    print(logtime, "***", logEntry, "***")
    return


def printFormErrors(form):
    """Print errors in submitted forms"""
    if form.errors:
        printLogEntry("Form errors:" + str(form.errors))
    return


def setToNoneIfEmptyString(parameter):
    """Set parameter to None if parameter is an emty string"""
    if len(parameter) == 0:
        parameter = None
    return parameter