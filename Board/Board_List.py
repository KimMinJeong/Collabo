<<<<<<< HEAD

=======
>>>>>>> master
from flask import Flask, render_template, request,\
    flash, request, g, session, redirect, url_for
from sqlalchemy import String, Integer, Sequence, Column
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base

import os

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:1234@localhost/pos'

db = SQLAlchemy(app)

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False))
Base = declarative_base()
Base.query = db_session.query_property()

class Board(db.Model):
    __tablename__='board'
    
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
        return '<Board %s,%s,%s,%s>' % self.category, self.subject,\
        self.status, self.contents,
        
db.create_all()
db.session.commit()


@app.route('/')
def top():
    return render_template('top.html')

@app.route('/board_list')
def board_list():
    g.board = Board.query.filter_by(category='store').first()
    
    return render_template('board_list.html')

@app.route('/board_insert', methods=['GET','POST'])
def board_insert():
 
    if request.method == 'POST':  
        category = request.form["category"]
        subject = request.form["subject"]
        status = request.form["status"]
        contents = request.form["contents"]
        
        db_insert = Board(category,subject , status , contents)
        db.session.add(db_insert)
        db.session.commit()
        
        return redirect(url_for('board_list'))
    return render_template('board_insert.html')


@app.route('/editor')
def editor():
    return render_template('editor.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0' ,port=int(os.environ.get('PORT',5000)))