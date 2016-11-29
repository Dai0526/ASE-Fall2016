# imports
from flask import Flask

from flask_sqlalchemy import SQLAlchemy
import os
from hashlib import md5
# create the application object
app = Flask(__name__)

# config
app.config.from_object('config.DevelopmentConfig')

# create the sqlalchemy object
db = SQLAlchemy(app)

#app.config.from_object(os.environ['APP_SETTINGS'])
from project.users.views import users_blueprint
from project.home.views import home_blueprint
from project.groups.views import groups_blueprint

# register our blueprints
app.register_blueprint(users_blueprint)
app.register_blueprint(home_blueprint)
app.register_blueprint(groups_blueprint)

def gravatar_url(email, size=80):
    """Return the gravatar image for the given email address."""
    return 'http://www.gravatar.com/avatar/%s?d=identicon&s=%d' % \
        (md5(email.strip().lower().encode('utf-8')).hexdigest(), size)

app.jinja_env.filters['gravatar'] = gravatar_url
