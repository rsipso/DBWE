from flask import Blueprint, render_template, redirect, url_for, flash, request
from forms import RegistrationForm, LoginForm
from models import db, User
from flask_login import login_user, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
#from flask_bcrypt import check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('list.index')) # Redirect logged in user to index

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title='Register', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('list.index')) # Redirect logged in user to index

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Login successful.', 'success')
            next_page = request.args.get('next') # Handle next parameter for redirects after login (if needed, import request from flask)
            return redirect(next_page) if next_page else redirect(url_for('list.index'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))