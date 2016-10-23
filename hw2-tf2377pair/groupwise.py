import os
import MySQLdb
from contextlib import closing
from flaskext.mysql import MySQL
from flask import Flask, request, session, g, redirect, url_for, \
			 abort, render_template, flash

# create app
mysql = MySQL()
app = Flask(__name__)
app.config['SECRET_KEY'] = '123456'
#app.config.from_object(__name__)
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '123456'
app.config['MYSQL_DATABASE_DB'] = 'groupwise'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql.init_app(app)
conn = mysql.connect()
cur = conn.cursor()

def get_db():
	if not hasattr(g, 'mysqldb'):
		g.mysqldb = mysql.connect()
	return g.mysqldb

def connect_db():
	connection = mysql.connect()
	connection.row_factory = mysql.row
	return connection

@app.before_request
def before_request():
	try:
		g.conn = mysql.get_db()
	except:
		print "fail to connect Database"
		import traceback; traceback.print_exc()
		g.conn = None

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
	entries = [dict(title = row[0],text=row[1]) for row in cur.fetchall()]
	return render_template('show_entries.html', entries = entries)

@app.route('/add', methods = ['POST'])
def add_entry():
	if not session.get('logged_in'):
		abort(401)
	title=request.form['title']
	txt=request.form['text']
#	print(ft+","+sn)
	cur.execute("INSERT INTO entries (title, text) VALUES (%s,%s);", (title,txt))
	conn.commit()
	flash('New Entries was posted')
	return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET' , 'POST'])
def login():
	error=None
	if request.method == 'POST':
		userName = request.form['username']
		userPass = request.form['password']
		cur.execute('select * from user where userName=(%s)',userName)
		row = cur.fetchall()

		if row is None:
			error = 'Invalid username'
		else:
			for pw in row:
				print pw
				if pw[2] != userPass:
					error = 'Invalid user password'
				else:
					session['logged_in'] = True
					flash('You are logged in')
					return redirect(url_for('show_entries'))

	return render_template('login.html', error = error)

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('show_entries'))


@app.route('/signup',methods=['GET', 'POST'])
def signup():
	error_signup = None
	if request.method == 'POST':
		userName_signup = request.form['username']
		userPass_signup = request.form['password']
		cur.execute('select * from user where userName=(%s)', userName_signup)
		output = cur.fetchone()

		if output is None:
			cur.execute('INSERT into user (userName, password) values (%s,%s);',(userName_signup,userPass_signup))
			conn.commit()
			flash('You are signed up')
			return redirect(url_for('login'))
		else:
			error_signup='username exists'
	return render_template('signup.html', error = error_signup)

if __name__ == '__main__':
	app.run()
