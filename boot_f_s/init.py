from flask import Flask, jsonify, render_template, request
from sqlalchemy import String , Integer, Sequence,Column
from sqlalchemy import create_engine
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:1234@localhost/pos'

db = SQLAlchemy(app)

class Boot(db.Model):
    __tablename__='boot_f'
    id= db.Column('info_id', db.Integer , primary_key=True)
    title = db.Column(db.String(30))
    text = db.Column(db.String(30))
    
    def __init__(self,title, text):
        self.title=title
        self.text=text
        
    def __repr(self):
        return '<boot_f %s %s>' % self.title , self.text
    
db.create_all()
db.session.commit()
    
@app.route('/')
def index():
    
    return render_template('boot_temp.html')

if __name__ == '__main__':
    app.run(debug=True)