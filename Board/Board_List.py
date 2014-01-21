from flask import Flask, jsonify, render_template, request
from sqlalchemy import String , Integer, Sequence,Column
from sqlalchemy import create_engine
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:1234@localhost/pos'

db = SQLAlchemy(app)

@app.route('/')
def index():
    return render_template('layout.html')

@app.route('/login')
def login():
    return render_template('index.html')
 
if __name__ == '__main__':
    app.run(debug=True)