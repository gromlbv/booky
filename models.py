from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from sqlalchemy.orm import Mapped, relationship


db = SQLAlchemy()

def migrate(app, db):
    Migrate(app, db)

def create_app(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
    app.config ["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    migrate(app, db)
    return app

def create_tables():
    db.create_all()



class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(24))
    password = db.Column(db.String(32))

    is_premium = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)
