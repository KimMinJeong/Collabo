# -*- coding: utf-8 -*-
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
import urllib
import hashlib
from config import *




app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
oid = OpenID(app, join(dirname(__file__), 'openid_store'))
#SQLALCHEMY_DATABASE_URI = 'postgres://uvkxbyzicejuyd:FzhZqstwa1YQ7FVPNAId0GO_4l@ec2-54-197-241-91.compute-1.amazonaws.com:5432/d22mrqavab61bp'

app.config.update(
        SQLALCHEMY_DATABASE_URI = 'postgres://uvkxbyzicejuyd:FzhZqstwa1YQ7FVPNAId0GO_4l@ec2-54-197-241-91.compute-1.amazonaws.com:5432/d22mrqavab61bp',
        #'postgresql://postgres:1111@localhost:5432/Board',
        SECRET_KEY = 'development key',
        DEBUG = True
    )



# def get_user():
#    return g.db.get('oid-' + session.get('openid', ''))


def init_db():    
    db.create_all()
    Base.metadata.create_all(bind=engine) 

  

@app.route('/')
def index():      
    return render_template('index.html')

#@app.before_request
#def before_request():
# if not 'id' in session:
#     flash(u'LogIN')    

@app.route('/top')
def top():
    return render_template('top.html')  

@app.route('/board_list')
def board_list():
    post_list =  Post.query.all()
    return render_template('board_list.html', post_list=post_list)

@app.route('/board_insert', methods=['GET','POST'])
def board_insert(): 
    if request.method == 'POST':  
        category = request.form["category"]
        subject = request.form["subject"]
        status = request.form["status"]
        contents = request.form["contents"]
        
        db_insert = Post(category, subject , status , contents)
        db.session.add(db_insert)
        db.session.commit()
        
        return redirect(url_for('board_list'))
    return render_template('board_insert.html')

@app.route('/editor')
def editor():
    return render_template('editor.html')   

@app.route('/login')
@oid.loginhandler
def login():
   #로그인을 하게 되면 바로 google 창이 뜰꺼야.
    pape_req = pape.Request([]) #what is pape_request???
    return oid.try_login("https://www.google.com/accounts/o8/id",
    ask_for=['email', 'fullname', 'nickname'])                                      
    #return render_template('example.html', next=oid.get_next_url(),
    #                       error=oid.fetch_error())


@oid.after_login
def after_login(resp):
    session['id'] = resp.identity_url
    if not session.get('id'):
        return redirect(oid.get_next_url())
    return redirect(url_for('board_list'))
    g.email = resp.email
    #그라바타 url이랑 email주소 리턴!
      
    gravatar = set_img(resp) 
    return redirect(url_for('contents', next=oid.get_next_url(),
                            name=resp.fullname or resp.nickname,
                            email=resp.email, gravata_url=gravatar[0],
                            email_gra=gravatar[1]))

@app.route('/add_comm', methods=['post'])
def add_comm():

    if request.method =='POST':
        email = request.form['email']
        comment = request.form['comment']
        db.session.add(Comment(email, comment))       
        db.session.commit()
    return redirect(oid.get_next_url())  
    

    
def set_img(resp):
    email_gra = resp.email
    size = 40
    gravatar_url = "http://www.gravatar.com/avatar/" + \
                    hashlib.md5(email_gra.lower()).hexdigest() + "?"
    gravatar_url += urllib.urlencode( {'d': 'mm' ,'s': str(size)} )     
    return gravatar_url, email_gra     
      
      
@app.route('/post')
def post():
    return render_template('example.html')

@app.route('/logout')
def logout():
    session.pop('id', None)
    flash(u'로그아웃!')
    return redirect(url_for('index'))

@app.route('/contents')
def contents():
    comm_list = Comment.query.all()
    return render_template('contents.html', comm_list=comm_list)
    


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=int(environ.get('PORT',5000)))