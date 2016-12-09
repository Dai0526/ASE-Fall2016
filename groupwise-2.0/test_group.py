import os
import unittest
from flask_testing import TestCase
import pytest
from project import app, db
from project.models import *

class GroupTestCase(TestCase):
    def create_app(self):
        app.config.from_object('config.TestConfig')
        return app

    def setUp(self):
        db.create_all()
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def login(self, username, password):
        return self.client.post('/login', data=dict(username=username, password=password), follow_redirects=True)

    def register(self, username, email, password1, password2):
        return self.client.post('/register', data=dict(username=username, email=email, password=password1, password2=password2), follow_redirects=True)

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
        return self.client.get( '/logout' , follow_redirects=True)

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
        rv = self.register('myname','abc@gmail.com', 'abc','abc')
        assert 'The username is already taken' in rv.data

    def test_logout(self):
        rv = self.logout()
        assert 'You were logged out' in rv.data

    def test_message(self):
        self.register('admin','abc@gmail.com','123456','123456')
        rv = self.login('admin','123456')
        rv = self.client.post('/add_message', data=dict(
        text='Hello World!'
        ), follow_redirects=True)
        assert 'No entries here so far' not in rv.data
        assert 'Hello World!' in rv.data


    def test_group(self):
        #login and create group
        self.register('myname', 'my@email', 'mypassword', 'mypassword')
        self.register('myname2', 'my2@email', 'mypassword2', 'mypassword2')
        self.register('myname3', 'my3@email', 'mypassword3', 'mypassword3')
        rv = self.login('myname','mypassword')
        rv = self.client.post('/creategroup', data=dict(groupname='groupname1',description='This is a description'), follow_redirects=True)
        assert 'You were successfully create a group' in rv.data

        # create a group without groupname
        rv = self.client.post('/creategroup', data=dict(groupname='',description='This is a description'), follow_redirects=True)
        assert 'You have to enter a groupname' in rv.data

         # create a group without description
        rv = self.client.post('/creategroup', data=dict(groupname='groupname4',description=''), follow_redirects=True)
        assert 'You have to enter a valid description' in rv.data

        #crete a group with the same groupname
        rv = self.client.post('/creategroup', data=dict(groupname='groupname1',description='This is a description'), follow_redirects=True)
        assert 'The groupname is already taken' in rv.data

        #add member succee
        self.client.get( '/groups/groupname1' , follow_redirects=True)
        rv = self.client.post('/groups/groupname1/add_member', data=dict(username='myname2'), follow_redirects=True)
        assert 'The member was added' in rv.data

        #add member that already in
        self.client.get( '/groups/groupname1' , follow_redirects=True)
        rv = self.client.post('/groups/groupname1/add_member', data=dict(username='myname2'), follow_redirects=True)
        assert 'User is already in group' in rv.data

        #add unregistered user
        self.client.get( '/groups/groupname1' , follow_redirects=True)
        rv = self.client.post('/groups/groupname1/add_member', data=dict(username='myname4'), follow_redirects=True)
        assert 'Invalid username' in rv.data

        rv=self.logout();
        rv = self.login('myname3','mypassword3')

    def test_event(self):
        #login and create group
        self.register('myname', 'my@email', 'mypassword', 'mypassword')
        self.register('myname2', 'my2@email', 'mypassword2', 'mypassword2')
        self.register('myname3', 'my3@email', 'mypassword3', 'mypassword3')
        self.register('myname4', 'my4@email', 'mypassword4', 'mypassword4')
        rv = self.login('myname','mypassword')
        rv = self.client.post('/creategroup', data=dict(groupname='groupname1',description='This is a description'), follow_redirects=True)
        assert 'You were successfully create a group' in rv.data

        #add member
        rv = self.client.post('/groups/groupname1/add_member',data=dict(username='myname3'),follow_redirects=True)
        assert 'The member was added' in rv.data
        assert 'Only members can add people!' not in rv.data
        assert 'User is already in group' not in rv.data

        #add same user should pop up message
        rv = self.client.post('/groups/groupname1/add_member',data=dict(username='myname3'),follow_redirects=True)
        assert 'User is already in group' in rv.data
        assert 'The member was added' not in rv.data
        assert 'Only members can add people!' not in rv.data

        # add event
        rv = self.login('myname3','mypassword3')
        rv = self.client.post('/groups/groupname1/add_event',data=dict(title='event2',text='description2'),follow_redirects=True)
        assert 'New event was added' in rv.data
        assert 'Only members can add events!' not in rv.data

        rv = self.client.get('/groups/groupname1/download', follow_redirects=True)
        assert 'event2' in rv.data

        #change user who is not in that group and add event
        self.logout()
        rv = self.login('myname2','mypassword2')
        rv = self.client.post('/groups/groupname1/add_event',data=dict(title='event1',text='description1'),follow_redirects=True)
        assert 'New event was added' not in rv.data
        assert 'Only members can add events!' in rv.data

        rv = self.client.post('/groups/groupname1/add_member',data=dict(username='myname4'),follow_redirects=True)
        assert 'User is already in group' not in rv.data
        assert 'The member was added' not in rv.data
        assert 'Only members can add people!' in rv.data

        rv = self.client.get('/groups/groupname1/download', follow_redirects=True)
        assert 'Only users in this group can download this file.' in rv.data

    def test_cache(self):
        self.register('myname', 'my@email', 'mypassword', 'mypassword')
        self.login('myname','mypassword')
        self.logout()
        # In add message
        rv = self.client.post('/add_message', data=dict(
        text='Hello World!'
        ), follow_redirects=True)
        assert 'You need to login first.' in rv.data
        # In create group
        rv = self.client.post('/creategroup', data=dict(
        groupname='groupname1',
        description='This is a description'
        ), follow_redirects=True)
        assert 'You need to login first.' in rv.data

        rv = self.client.get( '/groups' , follow_redirects=True)
        assert 'You need to login first.' in rv.data

if __name__ == '__main__':
    unittest.main()
