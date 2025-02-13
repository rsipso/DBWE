# app.py (Main Application File)

import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_required, current_user
from collections import defaultdict

from models import db, User, Project, ProjectParticipant, Expense  # Import from models.py
from forms import RegistrationForm, LoginForm, CreateProjectForm, AddExpenseForm, ShareProjectForm #Import forms
from views import index, register, login, logout, create_project, project, delete_project, delete_expense, remove_participant # Import from views.py


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)  # Initialize SQLAlchemy with the app
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Registering routes using functions from views.py ---
app.add_url_rule('/', view_func=index)
app.add_url_rule('/register', view_func=register, methods=['GET', 'POST'])
app.add_url_rule('/login', view_func=login, methods=['GET', 'POST'])
app.add_url_rule('/logout', view_func=logout)
app.add_url_rule('/create_project', view_func=create_project, methods=['GET', 'POST'])
app.add_url_rule('/project/<int:id>', view_func=project, methods=['GET', 'POST'])
app.add_url_rule('/delete_project/<int:project_id>', view_func=delete_project, methods=['POST'])
app.add_url_rule('/delete_expense/<int:expense_id>', view_func=delete_expense, methods=['POST'])
app.add_url_rule('/remove_participant/<int:project_id>/<int:user_id>', view_func=remove_participant, methods=['POST'])



if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables if they don't exist
    app.run(debug=True)