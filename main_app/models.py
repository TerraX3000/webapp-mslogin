from main_app import db, login_manager
from datetime import datetime

from flask_login import UserMixin

# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    print("Running load_user() with ", user_id)
    return Users.query.filter(Users.id == user_id).first()


# Define the User data-model
class Users(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(50), nullable=True)
    lastName = db.Column(db.String(50), nullable=True)
    position = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    # Define relationship between Users and Role using secondary table UserRoles
    # By referencing the secondary table, it is unnecessary to specify a relationship
    # between the Role and UserRole table
    roles = db.relationship(
        "Role",
        backref="users",
        lazy=True,
        passive_deletes=True,
        secondary="user_roles",
    )

    def __repr__(self):
        return f"Users('{self.firstName}','{self.lastName}','{self.email}')"


# Define the Role data-model
class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)


# Define the UserRoles association table
class UserRoles(db.Model):
    __tablename__ = "user_roles"
    id = db.Column(db.Integer(), primary_key=True)
    # Define foreign keys with Users and Role tables
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id", ondelete="CASCADE"))
    role_id = db.Column(db.Integer(), db.ForeignKey("roles.id", ondelete="CASCADE"))


class WebContent(db.Model):
    __tablename__ = "WebContent"
    id = db.Column(db.Integer, primary_key=True)
    sectionName = db.Column(db.String(255), nullable=True)
    contentName = db.Column(db.String(255), nullable=True)
    webContent = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return (
            f"WebContent('{self.sectionName}','{self.contentName}','{self.webContent}')"
        )


class adminSettings(db.Model):
    __tablename__ = "adminSettings"
    id = db.Column(db.Integer, primary_key=True)
    enableOpsMode = db.Column(db.Boolean, nullable=False, default=False)
    timestamp = db.Column(db.TIMESTAMP, nullable=False, default=datetime.now())