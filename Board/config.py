# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, g, session, flash, \
     redirect, url_for, abort
from flask_openid import OpenID
from openid.extensions import pape
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from os.path import dirname, join

app = Flask(__name__)
app.config.update(
        DATABASE_URI = 'postgresql://postgres:1111@localhost:5432/album',
        SECRET_KEY = 'development key',
        DEBUG = True
    )
"""openid 설치"""
oid = OpenID(app, join(dirname(__file__), 'openid_store'))

engine = create_engine(app.config['DATABASE_URI'])
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()
print Base.query
def init_db():
    Base.metadata.create_all(bind=engine)



