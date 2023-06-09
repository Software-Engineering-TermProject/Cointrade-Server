import os
from flask import Flask, render_template, request, redirect, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import Coin, Post, db, User
from flask_wtf.csrf import CSRFProtect
from Forms import BuycoinForm, PostForm, RegisterForm, LoginForm, DepositForm
from flask_wtf import FlaskForm

app = Flask(__name__)

#메인페이지
@app.route('/')
def main_page():
    userid = session.get('userid', None)
    form = BuycoinForm()

    if userid:
        user = User.query.filter_by(userid=userid).first()
        coin = Coin.query.get(1)
        remaining_coins = coin.marketCoin_count
    else:
        remaining_coins = None

    return render_template('main.html', form=form, userid=userid, remaining_coins=remaining_coins)

#마켓에서 코인구매
@app.route('/buyAtMarket', methods=['GET','POST'])
def buy_coin():
    userid = session.get('userid', None)
    if userid is None:
        return redirect('/login')
    
    if request.method == 'GET':
        # Show the form page
        return render_template('buyatmarket.html')
    else:
        coin_to_buy = int(request.form.get('coin_to_buy'))
        
        # 유효한 coin_id와 coin_to_buy를 받았는지 확인
        if not coin_to_buy or coin_to_buy <= 0:
            return "유효한 구매할 코인 수를 입력하세요.", 400

        coin = Coin.query.get(1)
        
        # 존재하는 코인인지 확인
        if coin is None:
            return "유효하지 않은 코인입니다.", 400
        
        user = User.query.filter_by(userid=userid).first()

        if coin.marketCoin_count < coin_to_buy:
            return "마켓에 충분한 코인이 없습니다.", 400

        if user.account_balance < coin_to_buy * coin.market_price:
            return "잔액이 부족합니다.", 405

        user.account_balance -= coin_to_buy * coin.market_price
        coin.marketCoin_count -= coin_to_buy
        user.coin_count += coin_to_buy

        db.session.commit()

        return redirect('/')



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

        coin = Coin(marketCoin_count=100, market_price=100)
        db.session.add(coin)

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
    if not userid:  # 로그인되어 있지 않은 경우
        return redirect('/login')
    
    users = User.query.all()
    return render_template('mypage.html', userid=userid, users=users)

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

#입금
@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    userid = session.get('userid', None)
    form = DepositForm()
    if form.validate_on_submit():
        if not userid:
            return redirect('/login')
        
        user = User.query.filter_by(userid=userid).first()
        
        if user.account_balance is None:  # account_balance가 None인 경우 초기값 설정
            user.account_balance = 0
        user.account_balance += form.data.get('account_balance')

        db.session.commit()

        return redirect('/mypage')
    
    return render_template('deposit.html', form=form, userid=userid)

#출금
@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    userid = session.get('userid', None)
    form = DepositForm()
    if form.validate_on_submit():
        if not userid:
            return redirect('/login')
        
        user = User.query.filter_by(userid=userid).first()
        
        withdraw_amount = form.data.get('account_balance')
        if user.account_balance is None or user.account_balance < withdraw_amount:
            # account_balance가 None인 경우 또는 출금하려는 금액이 잔액보다 많은 경우 출금할 수 없음
            return redirect('/mypage')
        user.account_balance -= withdraw_amount
        
        db.session.commit()

        return redirect('/mypage')
    
    if userid:
        user = User.query.filter_by(userid=userid).first()
        account_balance = user.account_balance if user.account_balance else 0
    else:
        account_balance = 0
        
    return render_template('withdraw.html', form=form, userid=userid, account_balance=account_balance)




# 마켓 페이지
@app.route('/market', methods=['GET'])
def market_page():
    userid = session.get('userid', None)
    posts = Post.query.all()
    form = FlaskForm()
    return render_template('market.html', posts=posts, userid=userid, form=form)    

# 게시물 작성
@app.route('/post', methods=['GET', 'POST'])
def create_post():
    userid = session.get('userid', None)
    form = PostForm()
    if form.validate_on_submit():
        
        post = Post()
        post.title = form.data.get('title')
        post.price = form.data.get('price')
        post.author = session.get('userid')  # 작성자 정보 추가

        db.session.add(post)
        db.session.commit()

        return redirect('/market')
        
    return render_template('post.html', form=form, userid=userid)

# 게시물 삭제
@app.route('/post/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    userid = session.get('userid', None)
    if not userid:
        return redirect('/')  # 유저가 로그인하지 않은 상태라면 메인 페이지로 리다이렉트
    
    post = Post.query.get_or_404(post_id)
    if post.author != userid:
        return redirect('/')  # 게시글의 작성자와 현재 로그인한 유저가 다르면 메인 페이지로 리다이렉트
    
    db.session.delete(post)
    db.session.commit()
    
    return redirect('/market')

#마켓 코인 구매
@app.route('/purchase/<int:post_id>', methods=['GET'])
def purchase(post_id):
    userid = session.get('userid', None)
    if not userid:  # 유저가 로그인하지 않은 상태라면 메인 페이지로 리다이렉트
        return redirect('/')
    
# 구매
@app.route('/post/<int:post_id>/buy', methods=['POST'])
def buy_post(post_id):
    userid = session.get('userid', None)
    if not userid:
        return redirect('/')  # 유저가 로그인하지 않은 상태라면 메인 페이지로 리다이렉트
    
    post = Post.query.get_or_404(post_id)
    user = User.query.filter_by(userid=userid).first()

    if user.account_balance < post.price:
        return redirect('/')  # 계정 잔고가 부족한 경우 메인 페이지로 리다이렉트
    
    user.account_balance -= post.price  # 계정 잔고 감소
    user.coin_count += int(post.title)  # 코인 수 증가

    db.session.delete(post)
    db.session.commit()
    
    return redirect('/market')


if __name__ == "__main__":
    basedir = os.path.abspath(os.path.dirname(__file__))  
    dbfile = os.path.join(basedir, 'db.sqlite') 
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfile
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False   
    app.config['SECRET_KEY']='asdfasdfasdfqwertx' #임의로 해시값 적용
    app.config['WTF_CSRF_ENABLED'] = True
    
    csrf = CSRFProtect(app)
    csrf.init_app(app)

    db.init_app(app)
    db.app = app
    with app.app_context():
        db.create_all()  
        
        if Coin.query.get(1) is None:
            coin = Coin(marketCoin_count=100, market_price=100)
            db.session.add(coin)
            db.session.commit()

    app.run(host='127.0.0.1', port=5000, debug=True) 