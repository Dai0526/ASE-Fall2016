from project import db
from project.models import *

db.drop_all()
db.create_all()

# Insertion
# user1 = User("wasabi","wa@com","12345")
# db.session.add(user1)
# db.session.add(User("saber", "fate@", "123"))
# db.session.add(Message("Hello, world",1))
# db.session.add(Message("Good", 2))

# Commit
db.session.commit()
