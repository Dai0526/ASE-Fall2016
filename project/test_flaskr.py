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

    def test_empty_db(self):
        rv = self.app.get('/')
        assert b'No entries here so far' in rv.data

    def login(self, username, password):
        return self.app.post( '/login' , data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get( '/logout' , follow_redirects=True)

    def test_login_logout(self):
        rv = self.login('admin','123456')
        assert 'You were logged in' in rv.data
        rv = self.login('rz','123456')
        assert 'Invalid username' in rv.data
        rv = self.login('admin','111111')
        assert 'Invalid password' in rv.data
        rv = self.logout()
        assert 'You were logged out' in rv.data

    def test_message(self):
        self.login('admin','123456')
        rv = self.app.post('/add', data=dict(
        title='<Hello>',
        text='<strong>HTML</strong> allowed here'
        ), follow_redirects=True)
        assert b'No entries here so far' not in rv.data
        assert b'&lt;Hello&gt;' in rv.data
        assert b'<strong>HTML</strong> allowed here' in rv.data


if __name__ == '__main__':
    unittest.main()