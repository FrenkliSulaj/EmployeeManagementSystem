from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean
from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='DepartmentUser')  # or 'Admin'
    is_admin = db.Column(db.Boolean, default=False) 
    is_approved = db.Column(db.Boolean, default=False)

    def is_admin(self):
        return self.role == 'Admin'
    
    from app import db

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100))