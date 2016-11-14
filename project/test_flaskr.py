import os
import tempfile
import unittest
import pytest
import flaskr

class FlaskrTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        flaskr.app.config['TESTING'] = True
        self.app = flaskr.app.test_client()
        with flaskr.app.app_context():
            flaskr.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(flaskr.app.config['DATABASE'])

    def login(self, username, password):
        return self.app.post('/login', data=dict(username=username, password=password), follow_redirects=True)

    def register(self, username, email, password1, password2):
        return self.app.post('/register', data=dict(username=username, email=email, password=password1, password2=password2), follow_redirects=True)

    def test_login(self):
        self.register('myname', 'my@email', 'mypassword', 'mypassword')
        #print rv.data
        rv = self.login('','mypassword')
        assert 'Invalid username' in rv.data
        rv = self.login('myname', 'p')
        assert 'Invalid password' in rv.data
        rv = self.login('myname','')
        assert 'Invalid password' in rv.data
        rv = self.login('myname','mypassword')
        assert 'You were logged in' in rv.data

    def logout(self):
        return self.app.get( '/logout' , follow_redirects=True)

    def test_register(self):
        rv = self.register('','abc@gmail.com','mypassword','mypassword')
        assert 'You have to enter a username' in rv.data
        rv = self.register('myname', 'abc', 'mypassword', 'mypassword')
        assert 'You have to enter a valid email address' in rv.data
        rv = self.register('myname', '', 'mypassword','mypassword')
        assert 'You have to enter a valid email address' in rv.data
        rv = self.register('myname', 'abc@gmail.com', '','')
        assert 'You have to enter a password' in rv.data
        rv = self.register('myname','abc@gmail.com', 'abc','acb')
        assert 'The two passwords do not match' in rv.data
        rv = self.register('myname','abc@gmail.com', 'abc','abc')
        assert 'You were successfully registered and can login now' in rv.data

    def test_logout(self):
        rv = self.logout()
        assert 'You were logged out' in rv.data

    def test_message(self):
        self.register('admin','abc@gmail.com','123456','123456')
        rv = self.login('admin','123456')
        rv = self.app.post('/add_message', data=dict(
        text='Hello World!'
        ), follow_redirects=True)
        assert 'No entries here so far' not in rv.data
        assert 'Hello World!' in rv.data

    def test_creategroup(self):
    	self.register('myname', 'my@email', 'mypassword', 'mypassword')
    	self.register('myname2', 'my2@email', 'mypassword2', 'mypassword2')
    	rv = self.login('myname','mypassword')
    	rv = self.app.post('/creategroup', data=dict(
        groupname='groupname1',
        description='This is a description'
        ), follow_redirects=True)

    	assert 'You were successfully create a group' in rv.data

    	rv = self.app.post('/creategroup', data=dict(
        groupname='groupname1',
        description='This is a description'
        ), follow_redirects=True)
        assert 'The groupname is already taken' in rv.data

        self.app.get( '/groups/groupname1' , follow_redirects=True)
        rv = self.app.post('/groups/groupname1/add_member', data=dict(
        username='myname2'
        ), follow_redirects=True)
        assert 'The member was added' in rv.data

        self.app.get( '/groups/groupname1' , follow_redirects=True)
        rv = self.app.post('/groups/groupname1/add_member', data=dict(
        username='myname2'
        ), follow_redirects=True)
        assert 'User was in that group' in rv.data

        self.app.get( '/groups/groupname1' , follow_redirects=True)
        rv = self.app.post('/groups/groupname1/add_member', data=dict(
        username='myname3'
        ), follow_redirects=True)
        assert 'Invalid username' in rv.data

    def test_cache(self):
        self.register('myname', 'my@email', 'mypassword', 'mypassword')
        self.login('myname','mypassword')
        self.logout()
        # In add message
        rv = self.app.post('/add_message', data=dict(
        text='Hello World!'
        ), follow_redirects=True)
        assert 'please login first' in rv.data
        # In create group
        rv = self.app.post('/creategroup', data=dict(
        groupname='groupname1',
        description='This is a description'
        ), follow_redirects=True)
        assert 'please login first' in rv.data

        rv = self.app.get( '/groups' , follow_redirects=True)
        assert 'please login first' in rv.data

if __name__ == '__main__':
    unittest.main()
