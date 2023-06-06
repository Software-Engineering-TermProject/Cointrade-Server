import os
from flask import Flask, render_template, request, redirect, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import Post, db, User
from flask_wtf.csrf import CSRFProtect
from Forms import PostForm, RegisterForm, LoginForm

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

#마이페이지
@app.route('/mypage', methods=['GET'])
def mypage():
    userid = session.get('userid', None)
    return render_template('mypage.html', userid=userid)

#마이페이지 상세정보
@app.route('/getMyInfo', methods=['GET'])
def getMyInfo():
    userid = session.get('userid', None)
    if not userid: # 로그인 x인 경우
        return jsonify({'error': 'Not logged in'}), 401
    
    user = User.query.filter_by(userid=userid).first()
    if user is None: # 유저가 db에 없는 경우
        return jsonify({'error': 'User not found'}), 404
    
    info = {
            'username': user.username,
            'account_balance': user.account_balance,  # 계좌 잔고
            'coin_count': user.coin_count,  # 보유 코인 수
            'coin_price': 100,  # 코인 가격
            'estimated_assets': user.account_balance + (user.coin_count * 100)  # 추정 자산
    }
    
    return jsonify(info)

# 마켓 페이지
@app.route('/market', methods=['GET'])
def market_page():
    userid = session.get('userid', None)
    posts = Post.query.all()
    return render_template('market.html', userid=userid, posts=posts)    

# 게시물 작성
@app.route('/post', methods=['GET', 'POST'])
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post()
        post.title = form.data.get('title')
        post.content = form.data.get('content')
        post.author = session.get('userid')  # 작성자 정보 추가

        db.session.add(post)
        db.session.commit()

        return redirect('/market')

    return render_template('post.html', form=form)

if __name__ == "__main__":
    basedir = os.path.abspath(os.path.dirname(__file__))  
    dbfile = os.path.join(basedir, 'db.sqlite') 
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfile
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False   
    app.config['SECRET_KEY']='asdfasdfasdfqwertx' #임의로 해시값 적용

    csrf = CSRFProtect(app)
    csrf.init_app(app)

    db.init_app(app)
    db.app = app
    with app.app_context():
        db.create_all()  

    app.run(host='127.0.0.1', port=5000, debug=True) 