# imports
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack, Response, Blueprint

from hashlib import md5
from werkzeug import check_password_hash, generate_password_hash
from functools import wraps
from flask_bootstrap import Bootstrap
from project.models import User
from project import app, db


# config
users_blueprint = Blueprint(
    'users', __name__,
    template_folder='templates'
)   # pragma: no cover

# login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user_id' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('users.login'))
    return wrap

@users_blueprint.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = db.session.query(User).filter_by(id=session['user_id']).first()

# route for handling the login page logic
@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if g.user:
        return redirect(url_for('home.timeline'))
    error = None
    if request.method == 'POST':
        user = db.session.query(User).filter_by(username=request.form['username']).first()
        if user is None:
            error = 'Invalid username'
        elif not check_password_hash(user.pw_hash, request.form['password']):
            error = 'Invalid password'
        else:
            flash('You were logged in')
            session['user_id'] = user.id
            return redirect(url_for('home.timeline'))
    return render_template('login.html', error=error)

@users_blueprint.route('/logout')
def logout():
    """Logs the user out."""
    flash('You were logged out')
    session.pop('user_id', None)
    return redirect(url_for('home.public_timeline'))

@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    """Registers the user."""
    if g.user:
        return redirect(url_for('home.timeline'))
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'You have to enter a username'
        elif not request.form['email'] or \
                '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif not request.form['password']:
            error = 'You have to enter a password'
        elif request.form['password'] != request.form['password2']:
            error = 'The two passwords do not match'
        elif db.session.query(User).filter_by(username=request.form['username']).first() is not None:
            error = 'The username is already taken'
        else:
            user = User(request.form['username'], request.form['email'], generate_password_hash(request.form['password']))
            db.session.add(user)
            db.session.commit()
            flash('You were successfully registered and can login now')
            return redirect(url_for('users.login'))
    return render_template('register.html', error=error)
