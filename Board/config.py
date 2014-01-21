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



