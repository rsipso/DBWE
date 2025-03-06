from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    lists_created = db.relationship('List', backref='creator', lazy=True)
    lists_participated = db.relationship('ListParticipant', backref='participant', lazy=True)
    items_added = db.relationship('Item', backref='added_by_user', lazy=True, foreign_keys='[Item.added_by_id]')
    items_ticked = db.relationship('Item', backref='ticked_by_user', lazy=True, foreign_keys='[Item.ticked_by_id]')

    def __repr__(self):
        return f'<User {self.username}>'

class List(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('Item', backref='list', lazy=True, cascade="all, delete-orphan") # Cascade for deleting items when list is deleted
    participants = db.relationship('ListParticipant', backref='list', lazy=True, cascade="all, delete-orphan") # Cascade for participants

    def __repr__(self):
        return f'<List {self.name}>'

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    list_id = db.Column(db.Integer, db.ForeignKey('list.id'), nullable=False)
    added_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_ticked = db.Column(db.Boolean, default=False)
    ticked_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    ticked_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<Item {self.name}>'

class ListParticipant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey('list.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ListParticipant List_id:{self.list_id} User_id:{self.user_id}>'