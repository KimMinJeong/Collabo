# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, g, session, flash, redirect, \
    url_for, jsonify, json
from flask.ext.sqlalchemy import SQLAlchemy
from flask_openid import OpenID
from functools import wraps, wraps
from os import environ
from os.path import dirname, join
from sqlalchemy import Column, Integer, String
from sqlalchemy.sql import functions
from sqlalchemy.types import DateTime, Boolean
import hashlib
import json
import os
import requests
import urllib


app = Flask(__name__)
oid = OpenID(app, join(dirname(__file__), 'openid_store'))
SQLALCHEMY_DATABASE_URI = os.environ.get(
                                         'DATABASE_URL','postgresql://postgres:1111@localhost:5432/postgres')
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SECRET_KEY'] = os.urandom(24)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
ACCESS_TOKEN = 'a122a18373551109d4bedaf55fd86545177380b7'
ORG = 'KimMinJeong'
REPO = 'Collabo'


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(Integer, primary_key=True)
    name = db.Column(db.String(60))
    email = db.Column(db.String(60))
    posts = db.relationship('Post', backref='author', 
                            cascade="all, delete-orphan", passive_deletes=True)
    comments = db.relationship('Comment', backref='user', 
                               cascade="all, delete-orphan", passive_deletes=True)
    authority = db.Column(db.Boolean, nullable=False, default='False')
    
    def __init__(self, name, email, authority):
        self.name = name
        self.email = email
        self.authority = authority
        
    def __repr__(self):
        return "<User id={0!r}, name={1!r}, email={2!r}, authority={3!r}>".\
                format(self.id, self.name, self.email, self.authority)
                
    
class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id',ondelete='cascade'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id',ondelete='cascade'))
    section = db.Column(db.Integer)
    created_at = db.Column(DateTime(timezone=True), nullable=False,
                                     default=functions.now())

    def __init__(self, comment, user_id, post_id, section):
        self.comment = comment
        self.user_id = user_id
        self.post_id = post_id
        self.section = section
        
    def __repr__(self):
        return "<Comment id={0!r},comment={1!r}, user_id={2!r}, post_id={3!r}, section={4!r}>".\
                format(self.id, self.comment, self.user_id, self.post_id, self.section)

    
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(Integer, primary_key=True)
    category = db.Column(db.String(10))
    subject = db.Column(db.String(50))
    status = db.Column(db.String(20))
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'))
    created_at = db.Column(DateTime(timezone=True),
                           nullable=False,
                           default=functions.now())
    comments = db.relationship('Comment', backref='post',
                               cascade="all, delete-orphan", 
                               passive_deletes=True)
    
    def __init__(self, category, subject, status, content, user_id):
        self.category = category
        self.subject = subject
        self.status = status
        self.content = content
        self.user_id = user_id
        
    def __repr__(self):
        return "<Post id={0!r}, category={1!r}, subject={2!r}, status={3!r}, content={4!r}> user_id={5!r}".\
                format(self.id, self.category, self.subject, self.status, self.content, self.user_id)


def init_db():
    db.create_all()
    

@app.before_request
def before_request():
    if not session.get('user_email') is None:
        g.user = User.query.filter_by(email=session.get('user_email')).first()


@app.route('/', methods=['GET'])
def log_in():      
    return render_template('index.html')


@app.route('/index', methods=['GET'])
def index():
    return render_template('identity.html')


def login_required(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if session.get('user_email') is None:
            flash(u'세션이 끊겼습니다.')
            return redirect(url_for('log_in',next=request.url))
        return f(*args,**kwargs)
    return decorated_function
        
        
@app.route('/login')
@oid.loginhandler
def login():
    return oid.try_login("https://www.google.com/accounts/o8/id",
          ask_for=['email', 'fullname', 'nickname'])
        
            
@app.route('/posts/lists')
@login_required
def board_list():
    post_list = Post.query.order_by(Post.id.desc()).all()
    return render_template('board_list.html', post_list=post_list)


@app.route('/posts/<int:id>', methods=['GET'])
@login_required
def show(id):    
    post = db.session.query(Post).get(id)
    return render_template('contents.html', post=post)


@app.route('/posts/<int:id>/put_post', methods=['POST'])
@login_required
def put_post(id):
    post = Post.query.get(id)
    post.status = request.values.get('status')
    if post.status == '개발예정':
        r = requests.post(
                         'https://api.github.com/repos/{0}/{1}/issues'.format(ORG, REPO),
                         auth=(ACCESS_TOKEN,
                               'x-oauth-basic'),
       data=json.dumps({'title':post.subject, 'body':post.content}))
        print r.headers['location']
    section = 10
    post.comments.append(Comment(comment=request.form['opinion'],
                                 user_id=g.user.id,
                                 post_id=session.get('post_id'),
                                 section=section))
    db.session.commit()
    return redirect(oid.get_next_url())


@app.route('/activation/<string:email>')
@login_required
def activity(email):
    info = User.query.filter(User.email==email).first()
    return render_template('current_activation.html', info=info)


@app.route('/posts/status', methods=['GET'])
@login_required
def board_detail():
    post_list = Post.query.all()
    return render_template('board_detail.html', post_list=post_list)


def set_color(status): 
    if status==u'대기중':
        return 'panel panel-info'
    elif status==u'개발예정':
        return 'panel panel-primary'
    elif status==u'업데이트':
        return 'panel panel-warning'
    elif status==u'개발중':
        return 'panel panel-success'
    elif status==u'반려':
        return 'panel panel-danger'
app.jinja_env.globals.update(set_color=set_color) 


@app.route('/register', methods=['POST'])
def add_user(account):
    email = account
    name = email.split('@')
    authority = False
    user = User(name[0],email,authority)
    db.session.add(user)
    db.session.commit()
    flash(u'처음 접속하셨습니다. 다시 한번 로그인 해주세요.')
    return redirect(url_for('log_in'))
    

@oid.after_login
def after_login(resp):   
    user = User.query.filter(User.email==resp.email).first() 
    if (resp.email.find('spoqa.com') > 0) and (user is None):
        add_user(resp.email)
        return redirect(url_for('log_in')) 
    elif (resp.email.find('spoqa.com') < 0):
        flash(u'접근권한이 없습니다. 관리자에게 문의하세요')
        return redirect(url_for('log_in')) 
    else:
        session['user_email'] = resp.email
        gravatar = set_img(resp.email)    
        session['gravatar'] = gravatar              
        return redirect(url_for('board_list')) 


def set_img(s):
    email_gra = s
    size = 40
    gravatar_url = "http://www.gravatar.com/avatar/" + \
                    hashlib.md5(email_gra.lower()).hexdigest() + "?"
    gravatar_url += urllib.urlencode( {'d': 'mm' , 's': str(size)} )     
    return gravatar_url
app.jinja_env.globals.update(set_img=set_img)     
    
    
@app.route('/posts', methods=['POST'])
def board_insert():
    category = request.form["category"]
    subject = request.form["subject"]
    status = request.form["status"]
    content = request.form["content"]   
    user_id = g.user.id
    db_insert = Post(category, subject, status, content, user_id)
    db.session.add(db_insert)
    db.session.commit()    
    return redirect(url_for('show', id=db_insert.id))


@app.route('/posts', methods=['GET'])
@login_required
def board_get():
    return render_template('board_insert.html')


@app.route('/posts/<int:id>', methods=['DELETE'])
def del_board(id):
    post = Post.query.get(id)
    db.session.delete(post) 
    db.session.commit()
    return jsonify(result='success')


@app.route('/posts/<int:id>/comment', methods=['POST'])
@login_required
def add_comm(id):
    if request.method =='POST':
        user_id = g.user.id
        comment = request.form['reply']
        post_id = id
        section = 99
        comment = Comment(comment, user_id, post_id, section)
        db.session.add(comment)       
        db.session.commit()
    return redirect(oid.get_next_url())


@app.route('/posts/comments/<int:id>', methods=['PUT'])
def update_comm(id):
    update = Comment.query.get(id)
    update.comment = request.form['comment_modify'] 
    db.session.commit()    
    return jsonify(result='success')


@app.route('/posts/comments/<int:id>', methods=['DELETE'])
def del_comm(id):
    comment = Comment.query.get(id)
    db.session.delete(comment)
    db.session.commit()
    return jsonify(dict(result='success'))


@app.route('/posts/<int:id>/modify', methods=['GET'])
@login_required
def get_modify(id):
    post = db.session.query(Post).get(id)
    return render_template('board_modify.html', post=post)


@app.route('/posts/<int:id>/modify', methods=['POST'])
def board_modify(id):
    update = Post.query.get(id)
    update.category = request.form["category"]
    update.subject = request.form["subject"]
    update.status = request.form["status"]
    update.content = request.form["content"]   
    update.user_id = g.user.id
    db.session.commit()
    return redirect(url_for('show',id=id))

    
@app.route('/logout')
def logout():
    session.pop('id',None)
    flash(u'로그아웃!')
    return redirect(url_for('log_in'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(environ.get('PORT',5000)))