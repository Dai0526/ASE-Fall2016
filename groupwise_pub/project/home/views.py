# imports
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack,make_response, Response, Blueprint
from flask_bootstrap import Bootstrap
from project import db
from project.models import *

from functools import wraps

# config
home_blueprint = Blueprint(
    'home', __name__,
    template_folder='templates'
)

@home_blueprint.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = db.session.query(User).filter_by(id=session['user_id']).first()

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

# use decorators to link the function to a url
@home_blueprint.route('/', methods=['GET', 'POST'])
def index():
    """Shows a users timeline or if no user is logged in it will
    redirect to the public timeline.  This timeline shows the user's
    messages as well as all the messages of followed users.
    """
#    if 'user_id' not in session:
#        return render_template('/login.html', error="please login first")
    if not g.user:
        return redirect(url_for('home.public_timeline'))
    messages = db.session.query(Message).filter_by(author_id=session['user_id']).order_by(Message.pub_date.desc()).limit(30).all()
    resp=make_response(render_template('pub_timeline.html', messages=messages))
#    resp.headers.add('Cache-Control','no-store,no-cache,must-revalidate,post-check=0,pre-check=0')
    return resp

@home_blueprint.route('/public')
def public_timeline():
    """Displays the latest messages of all users."""
    messages = db.session.query(Message).order_by(Message.pub_date.desc()).limit(30).all()
    return render_template('pub_timeline.html', messages=messages)

@home_blueprint.route('/my_timeline', methods=['GET', 'POST'])
def timeline():
    """Shows a users timeline or if no user is logged in it will
    redirect to the public timeline.  This timeline shows the user's
    messages as well as all the messages of followed users.
    """
    if 'user_id' not in session:
        return render_template('/login.html', error="please login first")
    if not g.user:
        return redirect(url_for('home.public_timeline'))
    messages = db.session.query(Message).filter_by(author_id=session['user_id']).order_by(Message.pub_date.desc()).limit(30).all()
    resp=make_response(render_template('timeline.html', messages=messages))
    resp.headers.add('Cache-Control','no-store,no-cache,must-revalidate,post-check=0,pre-check=0')
    return resp

@home_blueprint.route('/add_message', methods=['POST'])
@login_required
def add_message():
    """
    Registers a new message for the user.
    """
    if not g.user:
        abort(401)
    if request.form['text']:
        new_message = Message(request.form['text'], session['user_id'])
        db.session.add(new_message)
        db.session.commit()
        flash('Your message was recorded')
    return redirect(url_for('home.timeline'))

@home_blueprint.route('/<username>')
def user_timeline(username):
    if 'user_id' not in session:
        return render_template('/login.html', error="please login first")
    """Display's a users tweets."""
    profile_user = db.session.query(User).filter_by(username=username).first()
    if profile_user is None:
        abort(404)
    messages = db.session.query(Message).filter_by(author_id=profile_user.id).order_by(Message.pub_date.desc()).limit(30).all()
    resp=make_response(render_template('timeline.html', messages=messages, profile_user=profile_user))
    resp.headers.add('Cache-Control','no-store,no-cache,must-revalidate,post-check=0,pre-check=0')
    return resp
