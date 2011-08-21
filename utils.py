from database import connection, root

from functools import wraps
def _(str):
    """
    placeholder translation function
    """
    return str


def valid_login(username, password):
    """
    #XXX Must use hashing/salting
    """
    if connection['my_forum'].users.find_one(
            {'name': username, 'password': password}):
        return True
    else:
        return False


def get_cookie(fcn):
    @wraps
    def decorated(request, *args, **kwargs):
        if 'username' in request.cookies:
            session['username'] = request.cookies['username']
        fcn(request, *args, **kwargs)

    return decorated

def search_thread(id_thread, forum):
    for t in forum.threads:
        try:
            if str(t._id) == id_thread:
                return t
        except:
            if str(t['_id']) == id_thread:
                return t

    for f in forum.forums:
        r = search_thread(id_thread, f)
        if r:
            return r
    return False


def get_forum_by_path(forum_path=None):
    forum = root

    if forum_path:
        forums = forum_path.split('/')
        for i in forums:
            forum = filter(lambda x: x.name == i, forum.forums)[0]

    return forum

