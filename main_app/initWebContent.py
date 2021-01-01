def initializeWebContent(db, WebContent):
    """ Initialize webContent for first-time use """
    if not WebContent.query.first():
        importCSV = open(
            "main_app/WebContent_Example_Settings.csv",
            "r",
        )
        for row in importCSV:
            column = row.split(",")
            webContent = WebContent(
                sectionName=column[1].strip(),
                contentName=column[2].strip(),
                webContent=column[3].strip(),
            )
            db.session.add(webContent)
            db.session.commit()
            print(webContent)
        # logger.info("Added WebContent")
    return
