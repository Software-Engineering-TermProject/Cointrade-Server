from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model): 
    __tablename__ = 'user'   #테이블 이름 : user
    
    id = db.Column(db.Integer, primary_key = True)  
    userid = db.Column(db.String(32), unique=True, nullable=False)      
    username = db.Column(db.String(8), nullable=False)
    password = db.Column(db.String(8), nullable=False)     
    account_balance = db.Column(db.Integer, nullable=False, default=0)
    coin_count = db.Column(db.Integer, default=0)


class Post(db.Model):
    __tablename__ = 'post'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    #content = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    author = db.Column(db.String(32), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()