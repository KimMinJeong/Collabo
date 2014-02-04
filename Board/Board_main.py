# -*- coding: utf-8 -*-
from datetime import datetime, date, time
from flask import Flask, render_template, request, g, session, flash, redirect, \
    url_for, abort, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from flask_openid import OpenID
from openid.extensions import pape
from os import environ
from os.path import dirname, join
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import functions
from sqlalchemy.types import DateTime, Boolean
import hashlib
import urllib
import os


app = Flask(__name__)

#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
oid = OpenID(app, join(dirname(__file__), 'openid_store'))

SQLALCHEMY_DATABASE_URI = os.environ.get(
    'DATABASE_URL','postgresql://postgres:1234@localhost/pos')

db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SECRET_KEY'] = 'development keys'
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(60))
    email = db.Column(String(60))
    posts = db.relationship('Post', backref='author')
    comments = db.relationship('Comment', backref='reply')
    
    def __init__(self,name,email):
        self.name = name
        self.email = email
        
    def __repr__(self):
        return "<User id={0!r}, name={1!r}, email={2!r}>".\
                format(self.id, self.name, self.email)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    created_at = db.Column(DateTime(timezone=True), nullable=False,
                                     default=functions.now())
    
    def __init__(self, comment, user_id, post_id):
        self.comment = comment
        self.user_id = user_id
        self.post_id = post_id

    def __repr__(self):
        return "<Comment id={0!r},comment={1!r}, user_id={2!r}, post_id={3!r}>".\
                format(self.id, self.comment, self.user_id, self.post_id)

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(Integer, primary_key=True)
    category = db.Column(db.String(10))
    subject = db.Column(db.String(50))
    status = db.Column(db.String(20))
    contents = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(DateTime(timezone=True),
                           nullable=False,
                           default=functions.now())
    comments = db.relationship('Comment', backref='post')
    
    def __init__(self, category, subject, status, contents, user_id):
        self.category = category
        self.subject = subject
        self.status = status
        self.contents = contents
        self.user_id = user_id
        
    def __repr__(self):
        return "<Post id={0!r}, category={1!r}, subject={2!r}, status={3!r}, contents={4!r}> user_id={5!r}".\
                format(self.id, self.category, self.subject, self.status, self.contents, self.user_id)


def init_db():
    db.create_all()


@app.route('/')
def index():      
    return render_template('index.html')


@app.route('/login', methods=['get', 'POST'])
@oid.loginhandler
def login():
    return oid.try_login("https://www.google.com/accounts/o8/id",
          ask_for=['email','fullname','nickname'])
        
        
@app.route('/posts/lists')
def board_list():
    post_list = Post.query.all()
    return render_template('board_list.html', post_list=post_list)


@app.route('/posts/<int:id>', methods=['GET'])
def show(id):
    post = Post.query.filter(Post.id==id).first()
    comm_list = Comment.query.filter(Comment.post_id==id).all()
    gravatar = session.get('gravatar')
    return render_template('contents.html',
                            post=post,comm_list=comm_list)


@app.route('/posts/<int:id>', methods=['POST'])
def put_post(id):
    post = Post.query.get(id)
    post.status = request.values.get('status')
    post.admin_comments.append(Comment(email=session.get('email'), comment=request.form['comment']))
    db.session.commit()
    return redirect(oid.get_next_url())


@app.route('/posts/status', methods=['GET'])
def board_detail():
    post = Post.query.all()
    return render_template('board_detail.html',post=post)


@app.route('/register', methods=['GET'])
def register():    
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def add_user():
    email = request.form['newEmail']
    name = email.split('@')
    user = User(name[0],email)
    db.session.add(user)
    db.session.commit()
    flash(u'추가!')
    return redirect(oid.get_next_url())


@oid.after_login
def after_login(resp):      
    user = User.query.filter_by(email=resp.email).first()      
    if not user:
        return redirect(oid.get_next_url()) 
    gravatar = set_img(resp)
    flash(u'Successfully signed in')
    session['name'] = user.name
    session['email'] = resp.email    
    session['gravatar'] = gravatar[0]        
    return redirect(url_for('board_list'))

def set_img(resp):
    email_gra = resp.email
    size = 40
    gravatar_url = "http://www.gravatar.com/avatar/" + \
                    hashlib.md5(email_gra.lower()).hexdigest() + "?"
    gravatar_url += urllib.urlencode( {'d': 'mm' ,'s': str(size)} )     
    return gravatar_url, email_gra  


@app.route('/posts', methods=['POST'])
def board_insert(): 
    category = request.form["category"]
    subject = request.form["subject"]
    status = request.form["status"]
    contents = request.form["contents"]   
    user_id = session.get(User.id)
    
    db_insert = Post(category, subject, status, contents, user_id)
    db.session.add(db_insert)
    db.session.commit()
    return redirect(url_for('board_list'))


@app.route('/posts', methods=['GET'])
def board_get():
    return render_template('board_insert.html')


@app.route('/posts/<int:id>/comment', methods=['POST'])
def add_comm(id):#comment 추가
    if request.method =='POST':
        user_id = session.get('User.id')
        comment = request.form['reply']
        post_id = id
        img = session.get('gravatar')
        comment = Comment(comment, user_id, post_id)
        db.session.add(comment)       
        db.session.commit()
    return redirect(oid.get_next_url())


@app.route('/posts/comments/<int:id>', methods=['PUT'])
def update_comm(id):
    update = Comment.query.filter(Comment.id==id).first()
    update.comment = request.form['comment_modify']
    update.img=session.get('gravatar')
    db.session.commit()    
    return jsonify(dict(result='success'))


@app.route('/posts/comments/<int:id>', methods=['DELETE'])
def del_comm(id):
    comment = Comment.query.filter(Comment.id==id).first()
    db.session.delete(comment)
    db.session.commit()
    return jsonify(dict(result='success'))
    
    
@app.route('/logout')
def logout():
    session.pop('id', None)
    flash(u'로그아웃!')
    return redirect(url_for('index'))


@app.route('/edit')
def edit():
    return render_template('edit.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(environ.get('PORT',5000)))