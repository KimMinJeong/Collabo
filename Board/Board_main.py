# -*- coding: utf-8 -*-
from datetime import datetime, date, time
from flask import Flask, render_template, request, g, session, flash, redirect, \
    url_for, abort
from flask.ext.sqlalchemy import SQLAlchemy
from flask_openid import OpenID
from openid.extensions import pape
from os import environ
from os.path import dirname, join
from pip._vendor.distlib import metadata
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import functions
from sqlalchemy.types import DateTime, Boolean
import hashlib
import urllib



app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
oid = OpenID(app, join(dirname(__file__), 'openid_store'))

app.config.update(
        SQLALCHEMY_DATABASE_URI = 'postgres://uvkxbyzicejuyd:FzhZqstwa1YQ7FVPNAId0GO_4l@ec2-54-197-241-91.compute-1.amazonaws.com:5432/d22mrqavab61bp',
        SECRET_KEY = 'development key',
        DEBUG = True
    )

db = SQLAlchemy(app)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

#db settings
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], convert_unicode=True)

db_session =scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(60))
    email = Column(String(200))
    admin = Column(String(10))
    
    def __init__(self, name, email,admin):
        self.name = name
        self.email = email
        self.admin = admin
    def __repr__(self):
        return '<User %s,%s,%s,%s>' % self.name, self.email, self.admin


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200))
    comment = db.Column(db.String(500))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    created_at= db.Column(DateTime(timezone=True), nullable=False,
                                     default=functions.now())
    def __init__(self, email, comment, post_id):
        self.email = email
        self.comment = comment
        self.post_id = post_id
        
    def __repr__(self):
        return '<Comment %s %s %s>' % self.email, self.comment , self.post_id
    

class Post(db.Model):
    __tablename__='posts'
    id = db.Column(Integer, primary_key=True)
    category = db.Column(db.String(10))
    subject = db.Column(db.String(50))
    status = db.Column(db.String(20))
    contents = db.Column(db.String(500))
    author_id= db.Column(db.String(20))
    created_at= db.Column(DateTime(timezone=True), nullable=False,
                                     default=functions.now())
    comment_id = db.relationship('Comment', lazy='dynamic',backref='posts')

    def __init__(self,category,subject,status,contents, author_id):
        self.category = category
        self.subject = subject
        self.status = status
        self.contents = contents
        self.author_id = author_id
        
    def __repr__(self):
        return '<Post %s,%s,%s,%s, %s>' % self.category, self.subject,\
        self.status, self.contents, self.author_id


def init_db():    
    db.create_all()
    

@app.before_request
def before_request():
    g.user = None
    

@app.route('/')
def index():      
    return render_template('index.html')


@app.route('/board_top')
def top():
    return render_template('board_top.html')


@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    return oid.try_login("https://www.google.com/accounts/o8/id",
          ask_for=['email', 'fullname', 'nickname'])
        
        
@app.route('/post/lists')
def board_list():
    post_list =  Post.query.all()
    return render_template('board_list.html', post_list=post_list)



@app.route('/posts/<int:id>', methods=['GET'])
def show(id):
    posts= Post.query.filter(Post.id==id).first()
    comm_list = Comment.query.filter(Comment.post_id==id).all()    
    gravatar = session.get('gravatar')
    return render_template('contents.html',
                            posts=posts, comm_list=comm_list)


@app.route('/register')
def register():
    admin=User.query.filter(User.admin=='TRUE').all()
    if not session['email']==admin.email:
        abort(401)
        return redirect(oid.get_next_url())
    email=request.form['newEmail']
    name=email.split('@')
    user=User(name[0], email, False)
    db.session.add(user)
    db.session.commit()
    flash(u'추가!')
    return render_template('signup.html')


@oid.after_login
def after_login(resp):    
    user= User.query.filter_by(email=resp.email).first()  
    gravatar=set_img(resp)
    if user is not None:
        flash(u'Successfully signed in')
        g.user= user
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

        db_insert = Post(category, subject , status , contents, author_id)
        db.session.add(db_insert)
        db.session.commit()
        
        return redirect(url_for('board_list'))
    return render_template('board_insert.html')


#글 디테일뷰
@app.route('/posts/id/status', methods=['GET'])
def board_detail():
    post_detail = Post.query.all()
    return render_template('board_detail.html', post_detail=post_detail)


@app.route('/posts/<int:id>/detail/edit')
def admin():
    return render_template()


@app.route('/posts/<int:id>', methods=['post'])
def add_comm(id):#comment 추가
    if request.method =='POST':
        email = session.get('email')
        comment = request.form['comment']
        post_id = id
        db.session.add(Comment(email, comment, post_id))       
        db.session.commit()
    return redirect(oid.get_next_url())  

      
@app.route('/logout')
def logout():
    session.pop('id', None)
    flash(u'로그아웃!')
    return redirect(url_for('index'))




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(environ.get('PORT',5000)))