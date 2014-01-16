from flask import Flask, jsonify, render_template, request
from sqlalchemy import String , Integer, Sequence,Column
from sqlalchemy import create_engine
from flask.ext.sqlalchemy import SQLAlchemy

from sqlalchemy.ext.declarative import declarative_base


app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS' ,silent=True)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:1234@localhost/pos'

db = SQLAlchemy(app)

class info(db.Model):
    __tablename__ ='info'
    id = db.Column('info_id', db.Integer, primary_key=True)
    title = db.Column(db.String(40))
    text = db.Column(db.String(30))
    
    def __init__(self, title, text):
        self.title= title
        self.text = text
    def __repr(self):
        return '<info %s %s>' % self.title ,self.text

db.create_all()
db.session.commit()

a = db.session.info.query.all()
print a

@app.route('/get_db', methods=['GET']) 
def get_db():
    db = info.query.filter_by(title='Kim').first()
    return db

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)