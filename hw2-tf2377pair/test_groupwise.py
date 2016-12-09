import os
from hw2-tf2377pair import groupwise
import tempfile
import unittest

class GroupwiseTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, groupwise.app.config['DATABASE'] = tempfile.mkstemp()
        self.app = groupwise.app.test_client()


    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(groupwise.app.config['DATABASE'])
	


    def test_empty_db(self):
        rv = self.app.get('/')
        assert b'tiahhua' in rv.data

	def login(self, username, password):
		return self.app.post('/login', data=dict(username=username,password=password), follow_redirects=True)

	def logout(self):
		return self.app.get('/logout', follow_redirects=True)

	def test_login_logout(self):
		rv = self.login('tianhua', 'tianhua')
		assert 'You were logged in' in rv.data
		rv = self.logout()
		assert 'You were logged out' in rv.data
		rv = self.login('tianhuaf', '123456')
		assert 'Invalid username' in rv.data
		rv = self.login('tianhua', '123456')
		assert 'Invalid password' in rv.data
	def test_messages(self):
		self.login('admin', 'default')
		rv = self.app.post('/add', data=dict(title='<Hello>',text='<strong>HTML</strong> allowed here'), follow_redirects=True)
		assert 'No entries here so far' not in rv.data
		assert '&lt;Hello&gt;' in rv.data
		assert '<strong>HTML</strong> allowed here' in rv.data


if __name__ == '__main__':
	unittest.main()
