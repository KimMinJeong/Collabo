# -*- coding: utf-8 -*-
from config import *

# def get_user():
#    return g.db.get('oid-' + session.get('openid', ''))

@app.route('/')
def index():      
    return render_template('index.html')

@app.before_request
def before_request():
    if not 'openid' in session:
        flash(u'You have some problem..')    

   
    
@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    # if we are already logged in, go back to were we came from
    #if session.get('openid'):
    #    return redirect(oid.get_next_url())
    if request.method == 'POST':
        openid = request.form.get('openid')
        
        if openid:
            pape_req = pape.Request([]) #what is pape_request???
            return oid.try_login("https://www.google.com/accounts/o8/id",
            ask_for=['email', 'fullname', 'nickname'])
            
                                   
    return render_template('login.html', next=oid.get_next_url(),
                           error=oid.fetch_error())

@oid.after_login
def after_login(resp):
    session['openid'] = resp.identity_url
    if not session.get('openid'):
        return redirect(oid.get_next_url())
    return redirect(url_for('post', next=oid.get_next_url(),
                            name=resp.fullname or resp.nickname,
                            email=resp.email))

@app.route('/post')
def post():
    return render_template('example.html')
@app.route('/contents')
def contents():
    return render_template('contents.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(environ.get('PORT',5000)))