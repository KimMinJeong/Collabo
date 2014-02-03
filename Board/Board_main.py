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


app = Flask(__name__)
oid = OpenID(app, join(dirname(__file__),'openid_store'))
app.config.update(
        SQLALCHEMY_DATABASE_URI = 'postgres://uvkxbyzicejuyd:FzhZqstwa1YQ7FVPNAId0GO_4l@ec2-54-197-241-91.compute-1.amazonaws.com:5432/d22mrqavab61bp',
        SECRET_KEY = 'development key',
        DEBUG = True
)
db = SQLAlchemy(app)
app.config.from_envvar('FLASKR_SETTINGS',silent=True)


class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(60))
    email = Column(db.text,nullable=False)
    posts = db.relationship('Post',backref='author')
    comments = db.relationship('Comment',backref='comment')
    
    def __init__(self,name,email):
        self.name = name
        self.email = email
        
    def __repr__(self):
        return "<User id={0!r}, name={1!r}, email={2!r}>"\
            .format(self.id, self.name,self.email)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer,primary_key=True)
    comment_id = db.Column(db.String(50),db.ForeignKey('users.id'))
    comment = db.Column(db.text,nullable=False)
    post = db.relationship('Post',backref='comments')
    post_id = db.Column(db.Integer,db.ForeignKey('posts.id'))
    created_at= db.Column(DateTime(timezone=True),nullable=False,
                                     default=functions.now())
    
    def __init__(self,img,email,comment,post_id):
        self.img = img
        self.email = email
        self.comment = comment
        self.post_id = post_id
        
    def __repr__(self):
        return "<Comment id={0!r}, email={1!r}, comment_id={2!r}, comment={3!r}>"\
            .format(self.id, self.email, self.comment_id, self.comment)
    

class Post(db.Model):
    __tablename__='posts'
    id = db.Column(Integer,primary_key=True)
    category = db.Column(db.String(10))
    subject = db.Column(db.String(50))
    status = db.Column(db.String(20))
    contents = db.Column(db.text, nullable=False)
    author_id = db.Column(db.String(20), db.ForeignKey('users.id'))
    created_at = db.Column(DateTime(timezone=True),
                           nullable=False,
                           default=functions.now())
    comments = db.relationship('Comments', backref='post')
    
    def __init__(self,category,subject,status,contents,author_id):
        self.category = category
        self.subject = subject
        self.status = status
        self.contents = contents
        self.author_id = author_id
        
    def __repr__(self):
        return "<Post id={0!r}, category={1!r}, subject={2!r}, status={3!r}, contents={4!r}>".\
                format(self.id, self.category, self.subject, self.status, self.contents)
    
    
def init_db():
    db.create_all()


@app.route('/')
def index():      
    return render_template('index.html')


@app.route('/login', methods=['GET','POST'])
@oid.loginhandler
def login():
    return oid.try_login("https://www.google.com/accounts/o8/id",
          ask_for=['email','fullname','nickname'])
        
        
@app.route('/posts/lists')
def board_list():
    post_list = Post.query.all()
    return render_template('board_list.html',post_list=post_list)


@app.route('/posts/<int:id>',methods=['GET'])
def show(id):
    post= Post.query.filter(Post.id==id).first()
    comm_list = Comment.query.filter(Comment.post_id==id).all()
    gravatar = session.get('gravatar')
    return render_template('contents.html',
                            post=post,comm_list=comm_list)


@app.route('/posts/<int:id>',methods=['POST'])
def put_post(id):
    post= Post.query.get(id)
    post.status = request.values.get('status')
    post.admin_comments.append(Admin_Comments(email=session.get('email'),\
                                               comment=request.form['comment']))
    db.session.commit()
    return redirect(oid.get_next_url())


@app.route('/posts/status',methods=['GET'])
def board_detail():
    post = Post.query.all()
    return render_template('board_detail.html',post=post)


@app.route('/register',methods=['GET'])
def register():    
    return render_template('register.html')


@app.route('/register',methods=['POST'])
def add_user():
    email=request.form['newEmail']
    name=email.split('@')
    user=User(name[0],email)
    db.session.add(user)
    db.session.commit()
    flash(u'추가!')
    return redirect(oid.get_next_url())


@oid.after_login
def after_login(resp):      
    user= User.query.filter_by(email=resp.email).first()      
    if not user:
        return redirect(oid.get_next_url()) 
    gravatar=set_img(resp)
    flash(u'Successfully signed in')
    session['name'] = user.name
    session['email'] = resp.email    
    session['gravatar'] =gravatar[0]        
    return redirect(url_for('board_list'))

def set_img(resp):
    email_gra = resp.email
    size = 40
    gravatar_url = "http://www.gravatar.com/avatar/" + \
                    hashlib.md5(email_gra.lower()).hexdigest() + "?"
    gravatar_url += urllib.urlencode( {'d': 'mm' ,'s': str(size)} )     
    return gravatar_url, email_gra  


@app.route('/posts', methods=['GET','POST'])
def board_insert(): 
    if request.method == 'POST':  
        category = request.form["category"]
        subject = request.form["subject"]
        status = request.form["status"]
        contents = request.form["contents"]   
        author_id = session.get('name')        
        db_insert = Post(category,subject,status,\
                         contents,author_id)
        db.session.add(db_insert)
        db.session.commit()        
        return redirect(url_for('board_list'))
    return render_template('board_insert.html')


@app.route('/posts/<int:id>/comment',methods=['POST'])
def add_comm(id):#comment 추가
    if request.method =='POST':
        email = session.get('email')
        comment = request.form['reply']
        post_id = id
        img = session.get('gravatar')
        comment = Comment(img,email,comment,post_id)
        db.session.add(comment)       
        db.session.commit()
    return redirect(oid.get_next_url())


@app.route('/posts/comments/<int:id>',methods=['PUT'])
def update_comm(id):
    update= Comment.query.filter(Comment.id==id).first()
    update.comment= request.form['comment_modify']
    update.img=session.get('gravatar')
    db.session.commit()    
    return jsonify(dict(result='success'))


@app.route('/posts/comments/<int:id>',methods=['DELETE'])
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


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=int(environ.get('PORT',5000)))