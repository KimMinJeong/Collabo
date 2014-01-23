# -*- coding: utf-8 -*-
from config import *
from db import *
def init_db():
    db.create_all()
    Base.metadata.create_all(bind=engine)    

@app.route('/')
def index():      
    return render_template('index.html')


@app.route('/login')
@oid.loginhandler
def login():
   #로그인을 하게 되면 바로 google 창이 뜰꺼야.
    pape_req = pape.Request([]) #what is pape_request???
    return oid.try_login("https://www.google.com/accounts/o8/id",
    ask_for=['email', 'fullname', 'nickname'])                                      
    #return render_template('example.html', next=oid.get_next_url(),
    #                       error=oid.fetch_error())


@oid.after_login
def after_login(resp):
    session['id'] = resp.identity_url
    if not session.get('id'):
        return redirect(oid.get_next_url())
    g.email = resp.email
    #그라바타 url이랑 email주소 리턴!
    gravatar = set_img(resp)    
    return redirect(url_for('contents', next=oid.get_next_url(),
                            name=resp.fullname or resp.nickname,
                            email=resp.email, gravata_url=gravatar[0],
                            email_gra=gravatar[1]))

@app.route('/add_comm', methods=['post'])
def add_comm():

    if request.method =='POST':
        email = request.form['email']
        comment = request.form['comment']
        db_session.add(Comment(email, comment))       
        db_session.commit()
    return redirect(oid.get_next_url())  
    

    
def set_img(resp):
    email_gra = resp.email
    size = 40
    gravatar_url = "http://www.gravatar.com/avatar/" + \
                    hashlib.md5(email_gra.lower()).hexdigest() + "?"
    gravatar_url += urllib.urlencode( {'d': 'mm' ,'s': str(size)} )     
    return gravatar_url, email_gra     
      
      
@app.route('/post')
def post():
    return render_template('example.html')

@app.route('/logout')
def logout():
    session.pop('id', None)
    flash(u'로그아웃!')
    return redirect(url_for('index'))

@app.route('/contents')
def contents():
    comm_list = Comment.query.all()
    return render_template('contents.html', comm_list=comm_list)
    


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=int(environ.get('PORT',5000)))