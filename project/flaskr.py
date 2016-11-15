# all the imports
import os
import time
from sqlite3 import dbapi2 as sqlite3
from hashlib import md5
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack, Response
from werkzeug import check_password_hash, generate_password_hash

import logging
logging.basicConfig(level=logging.INFO)
# configuration
PER_PAGE = 30
DEBUG = True
SECRET_KEY = 'development key'

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'groupwise.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

#user class
class user(object):
    def __init__(self,un,pd,em):
        self.username=un
        self.pd=password
        self.em=em

    def get_userid(self,un):
        rv = query_db('select user_id from user where username = ?',
            [un], one=True)
        return rv[0] if rv else None

    def get_username(self):
        return self.username
    def get_password(self):
        return self.username
    def get_email(self):
        return self.email
    def set_username(self,un):
        self.username=un
    def set_password(self,pw):
        self.email=pw
    def set_email(self,em):
        self.email=em

#group class
class group(object):
    def __init__(self,gn,gd):
        self.groupname=gn
        self.gd=description

    def get_groupid(self,gn):
        rv = query_db('select group_id from group where groupname = ?',
            [gn], one=True)
        return rv[0] if rv else None

    def get_groupname(self):
        return self.groupname
    def get_description(self):
        return self.description

    def set_groupname(self,gn):
        self.username=gn
    def set_description(self,gd):
        self.email=gd



def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db'):
        top.sqlite_db = sqlite3.connect(app.config['DATABASE'])
        top.sqlite_db.row_factory = sqlite3.Row
    return top.sqlite_db
'''
def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db
'''
def connect_db():
	"""Connects to the specific database."""
	rv = sqlite3.connect(app.config['DATABASE'])
	rv.row_factory = sqlite3.Row
	return rv

@app.teardown_appcontext
def close_database(exception):
    """Closes the database again at the end of the request."""
    top = _app_ctx_stack.top
    if hasattr(top, 'sqlite_db'):
        top.sqlite_db.close()

def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
	"""Initializes the database."""
	init_db()
	print 'Initialized the database.'

def query_db(query, args=(), one=False):
    """Queries the database and returns a list of dictionaries."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv


def get_user_id(username):
    """Convenience method to look up the id for a username."""
    rv = query_db('select user_id from user where username = ?',
                  [username], one=True)
    return rv[0] if rv else None

def get_group_id(groupname):
    """Convenience method to look up the id for a groupname."""
    rv = query_db('select group_id from `group` where groupname = ?',
                  [groupname], one=True)
    return rv[0] if rv else None


def format_datetime(timestamp):
    """Format a timestamp for display."""
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')


def gravatar_url(email, size=80):
    """Return the gravatar image for the given email address."""
    return 'http://www.gravatar.com/avatar/%s?d=identicon&s=%d' % \
        (md5(email.strip().lower().encode('utf-8')).hexdigest(), size)


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = query_db('select * from user where user_id = ?',
                          [session['user_id']], one=True)

def after_this_request(func):
    if not hasattr(g,'call_after_request'):
        g.call_after_request=[]
    g.call_after_request.append(func)
    return func


def clear_cache():
    @after_this_request
    def delete_username_cookie(response):
        response.delete_cookie('username')
        return response

@app.after_request
def pre_request_callbacks(response):
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control']='no-store'
    return response

#show entries
@app.route('/')
def timeline():
    """Shows a users timeline or if no user is logged in it will
    redirect to the public timeline.  This timeline shows the user's
    messages as well as all the messages of followed users.
    """
    if not g.user:
        return redirect(url_for('public_timeline'))
    return render_template('timeline.html', messages=query_db('''
        select message.*, user.* from message, user
        where message.author_id = user.user_id and (
            user.user_id = ? or
            user.user_id in (select whom_id from follower
                                    where who_id = ?))
        order by message.pub_date desc limit ?''',
        [session['user_id'], session['user_id'], PER_PAGE]))

@app.route('/public')
def public_timeline():
    """Displays the latest messages of all users."""
    return render_template('timeline.html', messages=query_db('''
        select message.*, user.* from message, user
        where message.author_id = user.user_id
        order by message.pub_date desc limit ?''', [PER_PAGE]))


@app.route('/<username>')
def user_timeline(username):
    """Display's a users tweets."""
    profile_user = query_db('select * from user where username = ?',[username], one=True)
    if profile_user is None:
        abort(404)
    followed = False
    if g.user:
        followed = query_db('''select 1 from follower where
            follower.who_id = ? and follower.whom_id = ?''',
            [session['user_id'], profile_user['user_id']],
            one=True) is not None
    return render_template('timeline.html', messages=query_db('''
            select message.*, user.* from message, user where
            user.user_id = message.author_id and user.user_id = ?
            order by message.pub_date desc limit ?''',
            [profile_user['user_id'], PER_PAGE]), followed=followed,
            profile_user=profile_user)


@app.route('/<username>/follow')
def follow_user(username):
    """Adds the current user as follower of the given user."""
    if not g.user:
        abort(401)
    whom_id = get_user_id(username)
    if whom_id is None:
        abort(404)
    db = get_db()
    db.execute('insert into follower (who_id, whom_id) values (?, ?)',
              [session['user_id'], whom_id])
    db.commit()
    flash('You are now following "%s"' % username)
    return redirect(url_for('user_timeline', username=username))


@app.route('/<username>/unfollow')
def unfollow_user(username):
    """Removes the current user as follower of the given user."""
    if not g.user:
        abort(401)
    whom_id = get_user_id(username)
    if whom_id is None:
        abort(404)
    db = get_db()
    db.execute('delete from follower where who_id=? and whom_id=?',
              [session['user_id'], whom_id])
    db.commit()
    flash('You are no longer following "%s"' % username)
    return redirect(url_for('user_timeline', username=username))


@app.route('/add_message', methods=['POST'])
def add_message():
    if 'user_id' not in session:
        return  render_template('/login.html', error="please login first") 
    """Registers a new message for the user."""
    if 'user_id' not in session:
        abort(401)
    if request.form['text']:
        db = get_db()
        db.execute('''insert into message (author_id, text, pub_date)
          values (?, ?, ?)''', (session['user_id'], request.form['text'],
                                int(time.time())))
        db.commit()
        flash('Your message was recorded')
    return redirect(url_for('timeline'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Logs the user in."""
    if g.user:
        return redirect(url_for('timeline'))
    error = None
    if request.method == 'POST':
        user = query_db('''select * from user where
            username = ?''', [request.form['username']], one=True)
        if user is None:
            error = 'Invalid username'
        elif not check_password_hash(user['pw_hash'],
                                     request.form['password']):
            error = 'Invalid password'
        else:
            flash('You were logged in')
            session['user_id'] = user['user_id']
            return redirect(url_for('timeline'))
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registers the user."""
    if g.user:
        return redirect(url_for('timeline'))
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
        elif get_user_id(request.form['username']) is not None:
            error = 'The username is already taken'
        else:
            db = get_db()
            db.execute('''insert into user (
              username, email, pw_hash) values (?, ?, ?)''',
              [request.form['username'], request.form['email'],
               generate_password_hash(request.form['password'])])
            db.commit()
            flash('You were successfully registered and can login now')
            return redirect(url_for('login'))
    return render_template('register.html', error=error)

@app.route('/creategroup', methods=['GET', 'POST'])
def creategroup():
    if 'user_id' not in session:
        return  render_template('/login.html', error="please login first") 
    """Create a group."""
    #if not g.user:
        #return redirect(url_for('timeline'))
    error = None
    if request.method == 'POST':
        if not request.form['groupname']:
            error = 'You have to enter a groupname'
        elif not request.form['description']:
            error = 'You have to enter a valid description'

        elif get_group_id(request.form['groupname']) is not None:
            error = 'The groupname is already taken'
        else:
            db = get_db()
            db.execute('''insert into `group` (groupname, description) values (?, ?)''',
                [request.form['groupname'], request.form['description']])
            db.commit()
            group_id = get_group_id(request.form['groupname'])
            #group creater is the group manager by default
            db.execute('insert into manages (group_id, manager_id) values (?, ?)',
                [group_id, session['user_id']])
            db.commit()
            #creater is also a team member
            db.execute('''insert into `in` (group_id, member_id) values (?, ?)''',
                [group_id, session['user_id']])
            db.commit()
            flash('You were successfully create a group')
            return redirect(url_for('timeline'))
    return render_template('creategroup.html', error=error)

@app.route('/groups')
def groups():
    if 'user_id' not in session:
        return  render_template('/login.html', error="please login first") 
    """Displays the latest all groups."""
    return render_template('groups.html', groups=query_db('''
        select * from `group` order by group_id desc limit ?''', [PER_PAGE]))


@app.route('/my_group')
def my_group():
    """Displays the latest all groups."""
    if 'user_id' not in session:
        return  render_template('/login.html', error="please login first") 
    return render_template('my_group.html', mygroups=query_db('''
        select g.groupname, g.description from `group` g,user u, `in` i where i.group_id=g.group_id AND i.member_id=u.user_id AND u.user_id=? order by g.group_id desc limit ?''', [session['user_id'], PER_PAGE]))

@app.route('/gourps/<groupname>')
def group_info(groupname):
    if 'user_id' not in session:
        return  render_template('/login.html', error="please login first") 
    """Display members of groups."""
    profile_group = query_db('select * from `group` where groupname = ?',[groupname], one=True)
    if profile_group is None:
        abort(404)
    group_id = get_group_id(groupname)
    db = get_db()
    group_members = query_db('select i.member_id from `in` i where i.group_id=?', [group_id])
    db.commit()
    group_members = [i[0] for i in group_members]
    return render_template('groups.html', groupmembers=query_db('select * from user where user_id in ('
        + ', '.join('?'*len(group_members)) +') order by user_id desc limit 30',group_members), profile_group=profile_group)


@app.route('/groups/<groupname>/add_member', methods=['POST'])
def add_member(groupname):
    if 'user_id' not in session:
        return  render_template('/login.html', error="please login first") 
    """Registers a new member for the group."""
    if 'user_id' not in session:
        abort(401)
    user_id = get_user_id(request.form['username'])
    if user_id is None:
        flash('Invalid username')
    else:
        group_id = get_group_id(groupname)
        db = get_db()
        ex = query_db('select * from `in` where group_id = ? and member_id = ?',
            [group_id, user_id], one = True)
        db.commit()
        print ex
        if ex is not None:
            flash('User was in that group')
        else:
            db = get_db()
            db.execute('insert into `in` (group_id, member_id) values (?, ?)',
                [group_id, user_id])
            db.commit()
            flash('The member was added')
    return redirect(url_for('group_info', groupname=groupname))


@app.route('/my_gourp/<groupname>')
def my_group_info(groupname):
    if 'user_id' not in session:
        return  render_template('/login.html', error="please login first") 
    """Display members of groups."""
    profile_group = query_db('select * from `group` where groupname = ?',[groupname], one=True)
    if profile_group is None:
        abort(404)
    group_id = get_group_id(groupname)
    db = get_db()
    group_members = query_db('select i.member_id from `in` i where i.group_id=?', [group_id])
    db.commit()
    group_members = [i[0] for i in group_members]
    return render_template('my_group.html', groupmembers=query_db('select * from user where user_id in ('
        + ', '.join('?'*len(group_members)) +') order by user_id desc limit 30',group_members), profile_group=profile_group)


@app.route('/my_group/<groupname>/add_member', methods=['POST'])
def my_add_member(groupname):
    if 'user_id' not in session:
        return  render_template('/login.html', error="please login first") 
    """Registers a new member for the group."""
    if 'user_id' not in session:
        abort(401)
    user_id = get_user_id(request.form['username'])
    if user_id is None:
        flash('Invalid username')
    else:
        group_id = get_group_id(groupname)
        db = get_db()
        ex = query_db('select * from `in` where group_id = ? and member_id = ?',
            [group_id, user_id], one = True)
        db.commit()
        print ex
        if ex is not None:
            flash('User was in that group')
        else:
            db = get_db()
            db.execute('insert into `in` (group_id, member_id) values (?, ?)',
                [group_id, user_id])
            db.commit()
            flash('The member was added')
    return redirect(url_for('my_group_info', groupname=groupname))




@app.route('/logout')
def logout():
    """Logs the user out."""
    flash('You were logged out')
    session.pop('user_id', None)
    return redirect(url_for('public_timeline'))


# add some filters to jinja
app.jinja_env.filters['datetimeformat'] = format_datetime
app.jinja_env.filters['gravatar'] = gravatar_url

if __name__ == "__main__":
    app.run()

