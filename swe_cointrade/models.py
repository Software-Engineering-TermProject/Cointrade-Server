from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model): 
    __tablename__ = 'user'   #테이블 이름 : user
    
    id = db.Column(db.Integer, primary_key = True)  
    userid = db.Column(db.String(32), unique=True, nullable=False)      
    username = db.Column(db.String(8), nullable=False)
    password = db.Column(db.String(8), nullable=False)     

    #def __init__(self, username, password):
    #    self.set_username(username)
    #    self.set_password(password)
    
    #def set_password(self, password):
    #    self.password = generate_password_hash(password)
 
    #def check_password(self, password):
    #    return check_password_hash(self.password, password)