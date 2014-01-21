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
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1111@localhost:5432/ForFlask'
db = SQLAlchemy(app)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
#oid = OpenID(app, join(dirname(__file__), 'openid_store'))

@app.route('/')
def index():    
    return render_template('index.html')

@app.route('/login')
def login():
    return 1

@app.route('/ex')
def contents():
    return render_template('contents.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(environ.get('PORT',5000)))