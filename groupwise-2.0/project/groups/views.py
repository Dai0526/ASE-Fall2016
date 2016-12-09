# imports
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack, Response, Blueprint, make_response
from functools import wraps
from flask_bootstrap import Bootstrap
from project import db
from project.models import *



# config
groups_blueprint = Blueprint(
    'groups', __name__,
    template_folder='templates'
)

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

@groups_blueprint.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = db.session.query(User).filter_by(id=session['user_id']).first()

#@groups_blueprint.after_request
#def after_request(response):
#	response.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate')


@groups_blueprint.route('/creategroup', methods=['GET', 'POST'])
@login_required
def creategroup():
    if 'user_id' not in session:
        return  render_template('/login.html', error="please login first")
    """Create a group."""
    # if not g.user:
    #     return redirect(url_for('home.timeline'))
    error = None
    if request.method == 'POST':
        if not request.form['groupname']:
            error = 'You have to enter a groupname'
        elif not request.form['description']:
            error = 'You have to enter a valid description'
        elif Group.query.filter_by(groupname=request.form['groupname']).first() is not None:
            error = 'The groupname is already taken'
        else:
            group = Group(request.form['groupname'], request.form['description'])
            group.members = [g.user]
            #group,manager = [g.user]
            db.session.add(group)
            db.session.commit()

            # db = get_db()
            # db.execute('''insert into `group` (groupname, description) values (?, ?)''',
            #     [request.form['groupname'], request.form['description']])
            # db.commit()
            # group_id = get_group_id(request.form['groupname'])
            # #group creater is the group manager by default
            # db.execute('insert into manages (group_id, manager_id) values (?, ?)',
            #     [group_id, session['user_id']])
            # db.commit()
            # #creater is also a team member
            # db.execute('''insert into `in` (group_id, member_id) values (?, ?)''',
            #     [group_id, session['user_id']])
            # db.commit()
            flash('You were successfully create a group')
            return redirect(url_for('home.timeline'))
    resp= make_response(render_template('creategroup.html', error=error))
    resp.headers.add('Cache-Control', 'no-store,no-cache,must-revalidate,post-check=0,pre-check=0')
    return resp

@groups_blueprint.route('/groups')
@login_required
def groups():
    if 'user_id' not in session:
        return  render_template('/login.html', error="please login first")
    """Displays the latest all groups."""
    resp=make_response(render_template('groups.html', groups= db.session.query(Group).order_by(Group.fud_date.desc()).limit(30).all()))
    resp.headers.add('Cache-Control', 'no-store,no-cache,must-revalidate,post-check=0,pre-check=0')
    return resp
    #return render_template('groups.html',
    #    groups=
     #   db.session.query(Group).order_by(Group.fud_date.desc()).limit(30).all()
     #   )

@groups_blueprint.route('/my_group')
@login_required
def my_group():
    """Displays the latest all groups."""
    if 'user_id' not in session:
        return  render_template('/login.html', error="please login first")
    resp= make_response(render_template('my_group.html', mygroups=db.session.query(Group).filter(Group.members.any(id=session['user_id'])).all()))
    resp.headers.add('Cache-Control', 'no-store,no-cache,must-revalidate,post-check=0,pre-check=0')
    return resp

    #return render_template('my_group.html',
    #    mygroups=
    #    db.session.query(Group).filter(Group.members.any(id=session['user_id'])).all()
    #    )

@groups_blueprint.route('/groups/<groupname>')
@login_required
def group_info(groupname):
    #Display members of groups.
    if 'user_id' not in session:
        return  render_template('/login.html', error="please login first")
    profile_group = db.session.query(Group).filter_by(groupname=groupname).first()
    if profile_group is None:
        abort(404)
    resp= make_response(render_template('groups.html',
    	groupevents=db.session.query(Event).filter_by(group_id=profile_group.id).order_by(Event.pub_date.desc()).all(),
    	groupmembers=db.session.query(User).filter(User.groups.any(groupname=groupname)).all(),
    	profile_group=profile_group))
    resp.headers.add('Cache-Control', 'no-store,no-cache,must-revalidate,post-check=0,pre-check=0')
    return resp

@groups_blueprint.route('/groups/<groupname>/add_member', methods=['POST'])
@login_required
def add_member(groupname):
    if 'user_id' not in session:
        return  render_template('/login.html', error="please login first")
    group = db.session.query(Group).filter_by(groupname=groupname).first()
    user = db.session.query(User).filter_by(id=session['user_id']).first()
    if user not in group.members:
        flash('Only members can add people!')
    else:
        user = db.session.query(User).filter_by(username=request.form['username']).first()
        if user is None:
            flash('Invalid username')
        else:
            group = db.session.query(Group).filter_by(groupname=groupname).first()
            if user in group.members:
                flash('User is already in group')
            else:
                group.members.append(user)
                db.session.commit()
                flash('The member was added')
    return redirect(url_for('groups.group_info', groupname=groupname))

@groups_blueprint.route('/groups/<groupname>/add_event', methods=['POST'])
@login_required
def add_event(groupname):
    group = db.session.query(Group).filter_by(groupname=groupname).first()
    user = db.session.query(User).filter_by(id=session['user_id']).first()
    if user not in group.members:
        flash('Only members can add events!')
    else:
        new_event = Event(request.form['title'], request.form['text'], group.id, user.id)
        db.session.add(new_event)
        db.session.commit()
        flash('New event was added')
    return redirect(url_for('groups.group_info', groupname=groupname))

@groups_blueprint.route('/groups/<groupname>/download', methods=['GET'])
@login_required
def download(groupname):
    group = db.session.query(Group).filter_by(groupname=groupname).first()
    user = db.session.query(User).filter_by(id=session['user_id']).first()
    if user not in group.members:
        flash('Only users in this group can download this file.')
    else:
        profile_group = db.session.query(Group).filter_by(groupname=groupname).first()
        if profile_group is None:
            abort(404)
        groupevents= db.session.query(Event).filter_by(group_id=profile_group.id).all()
        csv = "\"title\",\"description\",\"author\",\"date\"\n"
        for event in groupevents:
            csv += "\"" + event.title + "\",\"" + event.description + "\",\"" + event.author.username + "\",\"" + str(event.pub_date) + "\"\n"
        return Response(
            csv,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=myplot.csv"}
            )
    return redirect(url_for('groups.group_info', groupname=groupname))

# @groups_blueprint.route('/my_gourp/<groupname>')
# @login_required
# def my_group_info(groupname):
#     # if 'user_id' not in session:
#     #     return  render_template('/login.html', error="please login first")
#     """Display members of groups."""
#     profile_group = query_db('select * from `group` where groupname = ?',[groupname], one=True)
#     if profile_group is None:
#         abort(404)
#     group_id = get_group_id(groupname)
#     db = get_db()
#     group_members = query_db('select i.member_id from `in` i where i.group_id=?', [group_id])
#     db.commit()
#     group_members = [i[0] for i in group_members]
#     return render_template('my_group.html', groupmembers=query_db('select * from user where user_id in ('
#         + ', '.join('?'*len(group_members)) +') order by user_id desc limit 30',group_members), profile_group=profile_group)


# @groups_blueprint.route('/my_group/<groupname>/add_member', methods=['POST'])
# @login_required
# def my_add_member(groupname):
#     # if 'user_id' not in session:
#     #     return  render_template('/login.html', error="please login first")
#     """Registers a new member for the group."""
#     if 'user_id' not in session:
#         abort(401)
#     user_id = get_user_id(request.form['username'])
#     if user_id is None:
#         flash('Invalid username')
#     else:
#         group_id = get_group_id(groupname)
#         db = get_db()
#         ex = query_db('select * from `in` where group_id = ? and member_id = ?',
#             [group_id, user_id], one = True)
#         db.commit()
#         print ex
#         if ex is not None:
#             flash('User was in that group')
#         else:
#             db = get_db()
#             db.execute('insert into `in` (group_id, member_id) values (?, ?)',
#                 [group_id, user_id])
#             db.commit()
#             flash('The member was added')
#     return redirect(url_for('groups.my_group_info', groupname=groupname))
