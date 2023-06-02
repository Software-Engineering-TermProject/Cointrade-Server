import os
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from models import db, User
from flask_wtf.csrf import CSRFProtect
from Forms import RegisterForm, LoginForm

app = Flask(__name__)

@app.route('/')
def main_page():
    userid = session.get('userid', None)
    return render_template('main.html', userid = userid)

#회원가입
@app.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit(): #유효성 검사. 내용 채우지 않은 항목이 있는지까지 체크
        user = User() 
        user.userid = form.data.get('userid')
        user.username = form.data.get('username')
        user.password = form.data.get('password')

        db.session.add(user) #DB저장
        db.session.commit() #변동사항 반영
        
        return redirect('/login') 
    return render_template('register.html', form=form)


#로그인
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm() #로그인폼
    if form.validate_on_submit(): #유효성 검사
        #print('{}가 로그인 했습니다'.format(form.data.get('userid')))
        session['userid']=form.data.get('userid') #form에서 가져온 userid를 세션에 저장
        return redirect('/') #성공하면 main.html로
    return render_template('login.html', form=form)


#로그아웃
@app.route('/logout', methods=['GET'])
def logout():
    session.pop('userid', None)
    return redirect('/')


@app.route('/market')
def market_page():
    return render_template('market.html')


if __name__ == "__main__":
    basedir = os.path.abspath(os.path.dirname(__file__))  
    dbfile = os.path.join(basedir, 'db.sqlite') 
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfile
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False   
    app.config['SECRET_KEY']='asdfasdfasdfqwertx' #임의로 해시값 적용

    csrf = CSRFProtect()
    csrf.init_app(app)

    db.init_app(app)
    db.app = app
    with app.app_context():
        db.create_all()  

    app.run(host='127.0.0.1', port=5000, debug=True) 