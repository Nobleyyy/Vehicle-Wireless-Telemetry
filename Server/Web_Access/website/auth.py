### Flask Auth ###

# Package Imports
from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

# File Imports
from .models import User
from . import db

auth = Blueprint('auth', __name__)

## Functions ##
@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Process login form
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        # Find user associated with the submitted email address
        user = User.query.filter_by(email=email).first()
        if user:
            # Check the password is correct against database
            if check_password_hash(user.password, password):
                # User logged in
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                # Redirect to the home page
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')
    # Display login page
    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    # Logout the current user
    logout_user()
    # Redirect to login page
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    # Process sign up form
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        # Check if account already exists
        user = User.query.filter_by(email=email).first()
        # Validate submitted details
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be at least 4 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be at least 2 characters.', category='error')
        elif password1 != password2:
            flash('Passwords do not match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            # Create new user
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method='pbkdf2:sha256'))
            # Add user to database
            db.session.add(new_user)
            db.session.commit()
            # Login new user
            login_user(user, remember=True)
            flash('Account created!', category='success')
            # Redirect to home page
            return redirect(url_for('views.home'))
    # Display sign up page
    return render_template("sign_up.html", user=current_user)