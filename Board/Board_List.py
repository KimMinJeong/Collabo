from flask import Flask, jsonify, render_template, request
from sqlalchemy import String , Integer, Sequence,Column
from sqlalchemy import create_engine
import os

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:1234@localhost/pos'



@app.route('/')
def top():
    return render_template('top.html')

@app.route('/board_list')
def board_list():
    return render_template('board_list.html')

@app.route('/board_insert')
def board_insert():
    return render_template('board_insert.html')
if __name__ == '__main__':
    app.run(debug=True, port=int(os.environ.get('PORT',5000)))