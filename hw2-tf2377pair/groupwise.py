import os
#import MySQLdb
#from flask_mysqldb import MySQL
from contextlib import closing
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
			 abort, render_template, flash

# create app
app=Flask(__name__)
app.config.from_object(__name__)

#config db
#db=MySQLdb.connect("localhost","root","123456","groupwise")
#cursor = db.cursor()
app.config.update(dict(
DATABASE='/tmp/groupwise.db',
DEBUG=True,
SECRET_KEY = 'development key',
USERNAME='admin',
PASSWORD= 'default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)



def connect_db():
	db=sqlite3.connect(app.config['DATABASE'])
	db.row_factory = sqlite3.Row
	return db
def get_db():
	if not hasattr(g,'sqlite_db'):
		g.sqlite_db = connect_db()
	return g.sqlite_db

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()




@app.before_request
def before_request():
	g.db=connect_db()
	

@app.teardown_appcontext 
def close_db(error):
	"""Closes the database again at the end of the request."""
	if hasattr(g, 'sqlite_db'): 
		g.sqlite_db.close()

def init_db():
	db = get_db()
	with app.open_resource('schema.sql', mode='r') as f: 
		db.cursor().executescript(f.read())
	db.commit()

#@app.cli.command('initdb') 
#def initdb_command():
#	"""Initializes the database."""
#	init_db()
#	print 'Initialized the database.' 


@app.route('/')
def show_entries():
	cur=g.db.execute('select title, text from entries order by id desc')
	entries=[dict(title=row[0],text=row[1]) for row in cur.fetchall()]
	return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
	if not session.get('logged_in'):
		abort(401)
	g.db.execute('insert into entries (title, text) values (?,?)', [request.form['title'],request.form['text']])
	g.db.commit()
	flash('New Entries was posted')
	return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET','POST'])
def login():
	error=None
	if request.method == 'POST':
		if request.form['username']!=app.config['USERNAME']:
			error='Invalid username'
		elif request.form['password']!=app.config['PASSWORD']:
			error='Invalid password'
		else:
			session['logged_in']=True
			flash('You are logged in')
			return redirect(url_for('show_entries'))
	return render_template('login.html',error=error)

@app.route('/logout')
def logout():
	session.pop('logged_in',None)
	flash('You were logged out')
	return redirect(url_for('show_entries'))

if __name__ =='__main__':
	app.run()