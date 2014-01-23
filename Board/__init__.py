from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_openid import OpenID
from os import environ
from os.path import dirname, join
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker


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

db = SQLAlchemy(app)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

#db settings

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], convert_unicode=True)

db_session =scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

 
    
class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200))
    comment = db.Column(db.String(500))

    def __init__(self, email, comment):
        self.email = email
        self.comment = comment

class Board(db.Model):
    __tablename__ = 'boards'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200))
    contents = db.Column(db.String(1000))
    title = db.Column(db.String(100))
    status = db.Column(db.String(50))


class Post(db.Model):
    __tablename__='posts'
    
    board_id = db.Column(Integer, primary_key=True)
    category = db.Column(db.String(10))
    subject = db.Column(db.String(50))
    status = db.Column(db.String(20))
    contents = db.Column(db.String(500))
   
    
    def __init__(self,category,subject,status,contents):
        self.category = category
        self.subject = subject
        self.status = status
        self.contents = contents
        
    def __repr__(self):
        return '<Post %s,%s,%s,%s>' % self.category, self.subject,\
        self.status, self.contents