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
        return redirect(url_for('list.index'))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        print(f"Login attempt for username: {username}") # LOG: Entered username

        user = User.query.filter_by(username=username).first()

        if user:
            print(f"User found in database: {user.username}, User ID: {user.id}") # LOG: User found
            print(f"Stored password hash (from DB): {user.password_hash}") # LOG: Stored hash

            password_check_result = check_password_hash(user.password_hash, password) # Werkzeug check_password_hash
            print(f"Password check result: {password_check_result}") # LOG: Comparison result

            if password_check_result:
                login_user(user)
                flash('Login successful.', 'success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('list.index'))
            else:
                print("Password check failed (incorrect password)") # LOG: Incorrect password
                flash('Login Unsuccessful. Please check username and password', 'danger')
        else:
            print(f"User not found in database for username: {username}") # LOG: User not found
            flash('Login Unsuccessful. Please check username and password', 'danger')

    return render_template('login.html', title='Login', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))