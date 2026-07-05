from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from . import models

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not email or not password:
            flash('Please enter both an email and a password.', 'error')
            return redirect(url_for('auth.login'))

        registered_password = models.users.get(email)
        if registered_password is None:
            flash('That email is not registered. Please sign up first.', 'error')
            return redirect(url_for('auth.login'))

        if password != registered_password:
            flash('Invalid password. Please try again.', 'error')
            return redirect(url_for('auth.login'))

        session['user'] = email
        flash(f'Welcome back, {email}!', 'success')
        return redirect(url_for('views.home'))

    return render_template('login.html')


@auth.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('views.home'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not email or not password:
            flash('Please enter both an email and a password.', 'error')
            return redirect(url_for('auth.sign_up'))

        if email in models.users:
            flash('That email is already registered. Please log in instead.', 'error')
            return redirect(url_for('auth.sign_up'))

        if password in models.users.values():
            flash('That password is already in use. Please choose a different password.', 'error')
            return redirect(url_for('auth.sign_up'))

        models.users[email] = password
        session['user'] = email
        flash('Your account has been created and you are signed in.', 'success')
        return redirect(url_for('views.home'))

    return render_template('sign_up.html')