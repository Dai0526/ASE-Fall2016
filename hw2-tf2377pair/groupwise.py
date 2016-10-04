import os
import MySQLdb
from flaskext.mysql import MySQL
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, \
			 abort, render_template, flash

# create app
mysql=MySQL()
app=Flask(__name__)
app.config['SECRET_KEY']='123456'
#app.config.from_object(__name__)
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '123456'
app.config['MYSQL_DATABASE_DB'] = 'groupwise'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql.init_app(app)
conn=mysql.connect()
cur=conn.cursor()

def get_db():
	if not hasattr(g,'mysqldb'):
		g.mysqldb=mysql.connect()
	return g.mysqldb

def connect_db():
	conn=mysql.connect()
	conn.row_factory=mysql.row
	return conn

@app.before_request
def before_request():
	try:
		g.conn=mysql.get_db()
	except:
		print "fail to connect Database"
		import traceback; traceback.print_exc()
		g.conn=None

@app.teardown_appcontext 
def teardown_request(exception):
	try:
		g.conn.close()
	except Exception as e:
		pass

@app.route('/')
def show_entries():
	#debug purpose
	print request.args
	cur.execute('select title, text from entries order by id desc')
	entries=[dict(title=row[0],text=row[1]) for row in cur.fetchall()]
	return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
	if not session.get('logged_in'):
		abort(401)
	ft=request.form['title']
	sn=request.form['text']
#	print(ft+","+sn)
	cur.execute("INSERT INTO entries (title, text) VALUES (%s,%s);", (ft,sn))
	print("commit")
	conn.commit()
	flash('New Entries was posted')
	return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET','POST'])
def login():
	error=None
	if request.method == 'POST':
		userName=request.form['username']
		userPass=request.form['password']
		cur.execute('select * from user where userName=(%s)',userName)
		row=cur.fetchall()

		if row is None:
			error='Invalid username'
		else: 
			for pw in row:
				print pw 
				if pw[2]!=userPass:
					error='Invalid user password'
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
