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


app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1111@localhost:5432/Board'
oid = OpenID(app, join(dirname(__file__), 'openid_store'))
app.config.update(
        DATABASE_URI = 'postgresql://postgres:1111@localhost:5432/Board',
        SECRET_KEY = 'development key',
        DEBUG = True
    )

db = SQLAlchemy(app)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

#db settings

engine = create_engine(app.config['DATABASE_URI'])

db_session =scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    email = Column(String(200))
    comment = Column(String(500))

    def __init__(self, email, comment):
        self.email = email
        self.comment = comment

class Board(Base):
    __tablename__ = 'boards'
    id = Column(Integer, primary_key=True)
    email = Column(String(200))
    contents = Column(String(1000))
    title = Column(String(100))
    status = Column(String(50))



