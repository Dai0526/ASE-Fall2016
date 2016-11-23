from project import db

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from datetime import datetime

class Message(db.Model):

    __tablename__ = "message"

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String, nullable=False)
    author_id = db.Column(db.Integer, ForeignKey('user.id'))
    pub_date = db.Column(db.DateTime)

    def __init__(self, description, author_id, pub_date=None):
        self.description = description
        self.author_id = author_id
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date

    def __repr__(self):
        return '<description %r>' % self.description


memberships = db.Table('Memberships',
    db.Column('group_id', db.Integer, db.ForeignKey('group.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model):
    """Class User in database"""
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False)
    pw_hash = db.Column(db.String)
    posts = db.relationship("Message", backref="author", lazy="dynamic")

    def __init__(self, username, email, pw_hash):
        self.username = username
        self.email = email
        self.pw_hash = pw_hash

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<user %r>' % self.username

class Group(db.Model):
    """docstring for Group"""
    __tablename__ = "group"

    id = db.Column(db.Integer, primary_key=True)
    groupname = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    fud_date = db.Column(db.DateTime)

    members = db.relationship("User", secondary=memberships,
        backref=db.backref("groups", lazy="dynamic"))

    def __init__(self, groupname, description, fud_date=None):
        self.groupname = groupname
        self.description = description
        if fud_date is None:
            fud_date = datetime.utcnow()
        self.fud_date = fud_date

    def __repr__(self):
        return '<Group %r>' % self.groupname
# retirve all user for a resturant
# User.query.filter(User.groups.any(name=name)).all()

