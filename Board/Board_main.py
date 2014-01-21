# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, g, session, flash, \
     redirect, url_for, abort, jsonify
from flask_openid import OpenID
from os import environ
from openid.extensions import pape
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from os.path import dirname, join
from flask.ext.sqlalchemy import SQLAlchemy



app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1111@localhost:5432/ForFlask'
oid = OpenID(app, join(dirname(__file__), 'openid_store'))
app.config.update(
        DATABASE_URI = 'postgresql://postgres:1111@localhost:5432/album',
        SECRET_KEY = 'development key',
        DEBUG = True
    )

db = SQLAlchemy(app)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)




# def get_user():
#    return g.db.get('oid-' + session.get('openid', ''))

@app.route('/')
def index():      
    return render_template('index.html')

@app.before_request
def before_request():
    if not 'openid' in session:
        flash(u'You have some problem..')
    else:
        flash(u'You logged in')

   
    
@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    # if we are already logged in, go back to were we came from
    #if session.get('openid'):
    #    return redirect(oid.get_next_url())
    if request.method == 'POST':
        openid = request.form.get('openid')
        
        if openid:
            pape_req = pape.Request([]) #what is pape_request???
            return oid.try_login("https://www.google.com/accounts/o8/id",
            ask_for=['email', 'fullname', 'nickname'])
            
                                   
    return render_template('login.html', next=oid.get_next_url(),
                           error=oid.fetch_error())

@oid.after_login
def after_login(resp):
    session['openid'] = resp.identity_url
    if not session.get('openid'):
        return redirect(oid.get_next_url())
    return redirect(url_for('post', next=oid.get_next_url(),
                            name=resp.fullname or resp.nickname,
                            email=resp.email))

@app.route('/post')
def post():
    return render_template('example.html')
@app.route('/contents')
def contents():
    return render_template('contents.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(environ.get('PORT',5000)))