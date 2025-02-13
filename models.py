# models.py (Database Models)

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()  # Create the SQLAlchemy instance (will be initialized with the app later)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    projects = db.relationship('Project', backref='creator', lazy='dynamic')
    participations = db.relationship('ProjectParticipant', back_populates='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    expenses = db.relationship('Expense', backref='project', lazy='dynamic', cascade="all, delete-orphan")
    participants = db.relationship('ProjectParticipant', back_populates='project', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Project {self.name}>'

class ProjectParticipant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project = db.relationship('Project', back_populates='participants')
    user = db.relationship('User', back_populates='participations')

    __table_args__ = (
        db.UniqueConstraint('project_id', 'user_id', name='_project_user_uc'),
    )
    def __repr__(self):
        return f'<ProjectParticipant project_id={self.project_id}, user_id={self.user_id}>'

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User')

    def __repr__(self):
        return f'<Expense {self.description} - ${self.amount}>'