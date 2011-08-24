#!/usr/bin/env python
from mongokit import Connection, Document, ObjectId
from datetime import datetime

import config

# connect to the database
connection = Connection( config.MONGODB_HOST, config.MONGODB_PORT)


#############
# MODELS
#############

class User(Document):
    structure = {
            'name': unicode,
            'email': unicode,
            'password': unicode,
            'creation_date': datetime,
            'allow_mails': bool,
            'signature': unicode,
            'group': unicode,
            'note': unicode,
            }
    use_dot_notation = True

    validators = {
            }

    def __repr__(self):
        return '<User %r>' % (self.name)


class Forum(Document):
    structure = {
            'name': unicode,
            'description': unicode,
            'forums': list,
            'threads': list,
            'locked': bool,
            }
    use_dot_notation = True

    validators = {
            }

    def __repr__(self):
        return '<Forum %r>' % (self.name)


class Thread(Document):
    structure = {
            '_id' : ObjectId,
            'title': unicode,
            'locked': bool,
            'comments': list,
            'pinned': bool,
            }
    use_dot_notation = True

    validators = {
            }

    def __repr__(self):
        return '<Thread %r>' % (self.title)


class Comment(Document):
    structure = {
            'author': ObjectId,
            'text': unicode,
            'creation_date': datetime,
            'edit_date': datetime,
            }
    use_dot_notation = True

    validators = {
            }

    def __repr__(self):
        return '<Comment %r>' % (self.text)


connection.register([User])
connection.register([Forum])
connection.register([Thread])
connection.register([Comment])

if not connection['my_forum'].forums.Forum.find_one():
    root = connection['my_forum'].forums.Forum()
    root.name = u'index'
    root.save()
else:
    root = connection['my_forum'].forums.Forum.find_one()


if not connection['my_forum'].users.User.find_one():
    admin = connection['my_forum'].users.User()
    admin.name = u'admin'
    admin.password = u'password'
    admin.save()

else:
    admin = connection['my_forum'].users.User.find_one()


