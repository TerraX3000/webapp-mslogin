from flask import Flask, url_for
from flask_session import Session
from importlib import import_module
import msal
from .config_msa import Config as app_config

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event, MetaData
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

# import pytz

# Third-party libraries for login authorization and management
# from authlib.integrations.flask_client import OAuth

from flask_login import LoginManager
from .log import logger, wrap, entering, exiting


def register_blueprints(app):
    for module_name in ["main", "ms_login", "errors", "admin"]:
        module = import_module(f"main_app.{module_name}.routes")
        # module_bp = module_name + "_bp"
        # blueprint = getattr(module, module_bp)
        # app.register_blueprint(blueprint)
        app.register_blueprint(module.bp)


# Included for MS login
def _build_auth_url(authority=None, scopes=None, state=None):
    return _build_msal_app(authority=authority).get_authorization_request_url(
        scopes or [],
        state=state or str(uuid.uuid4()),
        redirect_uri=url_for("ms_login.authorized", _external=True),
    )


# Included for MS login
def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        app_config.CLIENT_ID,
        authority=authority or app_config.AUTHORITY,
        client_credential=app_config.CLIENT_SECRET,
        token_cache=cache,
    )


# This function is necessary to perform cacade deletes in SQLite
@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# Instantiate the database
db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))
migrate = Migrate()
# Instantiate the login_manager
login_manager = LoginManager()
# Instantiate oauth for managing Google authentication
# oauth = OAuth()


# This function is used in jinja2 templates to display UTC datetime strings in local time
# def datetimefilter(value, format="%a %b %-d @ %-I:%M %p"):
#     tz = pytz.timezone("US/Eastern")  # timezone you want to convert to from UTC
#     utc = pytz.timezone("UTC")
#     value = utc.localize(value, is_dst=None).astimezone(pytz.utc)
#     local_dt = value.astimezone(tz)
#     return local_dt.strftime(format)


@wrap(entering, exiting)
def initializeSystemModeStatus(adminSettings):
    if not adminSettings.query.first():
        newAdminSettings = adminSettings(enableOpsMode=False)
        db.session.add(newAdminSettings)
        db.session.commit()
        logger.info("Initialized System Mode to 'Test'")
    return


@wrap(entering, exiting)
def initializeWebContent(WebContent):
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
        logger.info("Added WebContent")
    return


@wrap(entering, exiting)
def getWebContent(WebContent):
    """This function creates a dictionary for webContent data stored in the database.
    WebContent is accessed by calling this dictionary structure:
    {{ webContent[pageName][contentName] }}
    WebContent contains data stored in the SQL database which can be
    used to store information to customize app content.
    WebContent is accessible by all templates by referencing
    the WebContent dictionary."""
    webContentDB = WebContent.query.all()
    webContent = {}
    for content in webContentDB:
        if content.sectionName in webContent:
            # print("sectionName found: ", content.sectionName)
            if content.contentName in webContent[content.sectionName]:
                # print("blockname found: ", content.contentName)
                webContent[content.sectionName][
                    content.contentName
                ] = content.webContent
            else:
                # print("new blockname: ", content.contentName)
                webContent[content.sectionName][
                    content.contentName
                ] = content.webContent
        else:
            # print("new sectionName: ", content.sectionName)
            webContent[content.sectionName] = {content.contentName: content.webContent}
    # print("webContent: ", webContent)
    return webContent


@wrap(entering, exiting)
def createAccessRoles(Role):
    """ Initialize app with access roles for Guest, User, and Admin """
    if not Role.query.first():
        for role_name in ["Guest", "User", "Admin"]:
            role = Role(name=role_name)
            db.session.add(role)
        db.session.commit()
        logger.info("Added default access roles")
    return


@wrap(entering, exiting)
def createTestUser(Users):
    """ Initialize app with test user """
    # Create 'test@test' user with 'Admin' role
    if not Users.query.first():
        user = Users(
            firstName="test",
            lastName="test",
            position="test",
            email="test@test",
        )
        db.session.add(user)
        db.session.commit()
        logger.info("Added test user")
        return user
    return None


@wrap(entering, exiting)
def createTestUserRole(UserRoles, user):
    """ Initialize app with test user with admin access """
    user_roles = UserRoles(user_id=user.id, role_id=3)
    db.session.add(user_roles)
    db.session.commit()
    logger.info("Added admin access for test user")
    return


def create_app(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.jinja_env.globals.update(zip=zip)
    # app.jinja_env.filters["datetimefilter"] = datetimefilter
    # Import logging

    # Initialize the database with the app
    db.init_app(app)
    # Initialize Migrate with the app and the database
    migrate.init_app(app, db)
    # Create all database tables
    from main_app.models import Users, UserRoles, Role, WebContent, adminSettings

    with app.app_context():
        db.create_all()

    # Add context processor to make webContent data stored in the database
    # available to all templates by default

    with app.app_context():
        initializeSystemModeStatus(adminSettings)
        initializeWebContent(WebContent)

    @app.context_processor
    def setWebContentAppContext():
        return dict(webContent=getWebContent(WebContent))

    # Set up for using Google Login and API (if running on Google Cloud)
    useGoogleLoginAndAPI = app.config.get("USE_GOOGLE_LOGIN_AND_API")
    print("useGoogleLoginAndAPI =", useGoogleLoginAndAPI)
    if useGoogleLoginAndAPI:
        pass
        # User session management setup
        # https://flask-login.readthedocs.io/en/latest
        # login_manager.init_app(app)

        # OAuth 2 client setup
        # GOOGLE_DISCOVERY_URL = (
        #     "https://accounts.google.com/.well-known/openid-configuration"
        # )
        # oauth.init_app(app)
        # oauth.register(
        #     name="google",
        #     server_metadata_url=GOOGLE_DISCOVERY_URL,
        #     client_kwargs={"scope": "openid email profile"},
        # )

    # Initialize Session for MS login
    Session(app)
    login_manager.init_app(app)

    # Create test account for initial use
    from main_app.models import Users, Role, UserRoles

    with app.app_context():
        createAccessRoles(Role)
        test_user = createTestUser(Users)
        if test_user:
            createTestUserRole(UserRoles, test_user)

    # This section is needed for url_for("foo", _external=True) to automatically
    # generate http scheme when this sample is running on localhost,
    # and to generate https scheme when it is deployed behind reversed proxy.
    # See also https://flask.palletsprojects.com/en/1.0.x/deploying/wsgi-standalone/#proxy-setups
    from werkzeug.middleware.proxy_fix import ProxyFix

    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # Included for MS login
    app.jinja_env.globals.update(_build_auth_url=_build_auth_url)  # Used in template

    register_blueprints(app)

    return app
