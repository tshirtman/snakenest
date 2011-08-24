#)!/usr/bin/env python
#http://flask.pocoo.org/docs/quickstart

from flask import Flask
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask import redirect
from flask import flash
from flask import make_response
from flask import abort

from datetime import datetime

import config

app = Flask(__name__)
app.config.from_object(config)
# FIXME find why this is not automatic
app.secret_key = config.secret_key

from database import User, Forum, Thread, Comment, connection, ObjectId, root

from utils import _, get_cookie, valid_login, search_thread, get_forum_by_path

#@get_cookie
@app.route('/')
def index():
    return render_template('forum.html',
            title='index',
            forum=root)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if valid_login(
                request.form['username'],
                request.form['password']):
                session['username'] = request.form['username']

                flash(_('you are now connected as ' +
                    request.form['username']))
                resp = make_response(index())

                if request.form.get('cookie', False):
                    resp.set_cookie('username', request.form['username'])
                return resp
        else:
            flash(_("invalid username or password"))
            return render_template('login.html')

    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@get_cookie
@app.route('/<path:forum_path>/')
def forum(forum_path):
    try:
        return render_template('forum.html', forum=get_forum_by_path(forum_path))
    except IndexError:
        raise
        #abort(404)

@get_cookie
@app.route('/<path:forum_path>/delete')
def delete_forum(forum_path):
    parent_path = forum_path.split('/')[:-1]
    parent = get_forum_by_path('/'.join(parent_path))
    for i, x in enumerate(parent.forums):
        if x['name'] == forum_path.split('/')[-1]:
            parent['forums'].pop(i)
            break

    root.save()
    return redirect(parent_path)


@app.route('/new_forum', methods=['GET', 'POST'])
def new_root_forum():
    c = connection['my_forum']
    forum = root

    if request.method == 'GET':
        return render_template('new_forum.html', forum=forum)

    elif request.method == 'POST':
        new_forum = c.forums.Forum()
        new_forum.name = request.form['name']
        forum.forums.append(new_forum)
        root.save()

        return redirect(request.form['name'])


@app.route('/<path:forum_path>/new_forum', methods=['GET', 'POST'])
def new_forum(forum_path):
    c = connection['my_forum']
    forum = get_forum_by_path(forum_path)

    if request.method == 'GET':
        return render_template('new_forum.html', forum=forum)

    elif request.method == 'POST':
        new_forum = c.forums.Forum()
        new_forum.name = request.form['name']
        forum['forums'].append(new_forum)
        root.save()

        return redirect('/' + forum_path + '/' + request.form['name'])


@app.route('/new_thread', methods=['GET', 'POST'])
def new_root_thread():
    c = connection['my_forum']
    forum = root

    if request.method == 'GET':
        return render_template('new_thread.html', forum=forum)

    elif request.method == 'POST':
        user = connection['my_forum'].users.User.find_one(
                {'name': session['username']})

        new_thread = c.threads.Thread()
        new_thread._id = ObjectId()
        new_thread.title = request.form['title']
        new_thread.pinned = False
        comment = c.comments.Comment()
        comment.author = user._id
        comment.text = request.form['text']
        comment.creation_date = datetime.today()
        new_thread.comments.append(comment)
        forum.threads.append(new_thread)
        root.save()

        return redirect('/thread/' + str(new_thread._id))


@app.route('/<path:forum_path>/new_thread', methods=['GET', 'POST'])
def new_thread(forum_path):
    c = connection['my_forum']
    forum = get_forum_by_path(forum_path)

    if request.method == 'GET':
        return render_template('new_thread.html', forum=forum)

    elif request.method == 'POST':
        user = connection['my_forum'].users.User.find_one(
                {'name': session['username']})

        new_thread = c.threads.Thread()
        new_thread._id = ObjectId()
        new_thread.title = request.form['title']
        new_thread.pinned = False
        comment = c.comments.Comment()
        comment.author = user._id
        comment.text = request.form['text']
        comment.creation_date = datetime.today()
        new_thread.comments.append(comment)
        forum.threads.append(new_thread)
        root.save()

        return redirect('/'+ forum_path + '/thread/' + str(new_thread._id))


@app.route('/<path:forum_path>/thread/<string:id_thread>')
def thread(forum_path=None, id_thread=None):
    forum = get_forum_by_path(forum_path)
    t = [x for x in forum['threads'] if str(x['_id']) == id_thread][0]
    return render_template('thread.html',
            forum=forum,
            thread=t)


@app.route('/thread/<string:id_thread>/respond',
        methods=['GET', 'POST'])
def respond_arbitraty_thread(id_thread=None):
    c = connection['my_forum']
    t = search_thread(id_thread, root)

    if not t:
        abort(404)

    if request.method == 'GET':
        # XXX
        return redirect('/thread/' + str(t['_id']))

    elif request.method == 'POST':
        if not t['locked']:
            user = connection['my_forum'].users.User.find_one(
                    {'name': session['username']})

            comment = c.comments.Comment()
            comment.author = user._id
            comment.text = request.form['text']
            comment.creation_date = datetime.today()
            t['comments'].append(comment)
            root.save()

        return redirect('/thread/' + str(id_thread))


@app.route('/<path:forum_path>/thread/<string:id_thread>/respond',
        methods=['GET', 'POST'])
def respond(forum_path=None, id_thread=None):
    c = connection['my_forum']
    forum = get_forum_by_path(forum_path)
    t = [x for x in forum['threads'] if str(x['_id']) == id_thread][0]
    if request.method == 'GET':
        # XXX
        return redirect('/' + forum_path + '/thread/' + str(t['_id']))

    elif request.method == 'POST':
        if not t['locked']:
            user = connection['my_forum'].users.User.find_one(
                    {'name': session['username']})

            comment = c.comments.Comment()
            comment.author = user._id
            comment.text = request.form['text']
            comment.creation_date = datetime.today()
            t['comments'].append(comment)
            root.save()

        return redirect('/' + forum_path + '/thread/' + str(t['_id']))


@app.route('/user/<int:id_user>')
def user(id_user):
    pass


@app.template_filter()
def user_name(id_user):
    return connection['my_forum'].users.User.find_one({'_id': id_user}).name

if __name__ == '__main__':
    app.run(
            host='0.0.0.0',
            debug=True)


