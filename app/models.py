from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown
import bleach
from flask import current_app, request, url_for, flash
from flask_login import UserMixin, AnonymousUserMixin 
import uuid 
from decimal import Decimal

from app.exceptions import ValidationError 
from . import db, login_manager 


class Permission:
    ADMIN = 16 

Roles_Table = {} 
Roles_Table[1] = {'name': 'User', 'default': 1, 'permission':0} 
Roles_Table[2] = {'name': 'Administrator', 'default': 0, 'permission':16}


class User(UserMixin):
    
    def __init__(self, **kwargs):
        super(User, self).__init__()   
 
        self.email = kwargs['email'] 
        self.username = kwargs['user_name'] 

        if 'raw_password' in kwargs: ## for first time user registration 
            self.id = self.generate_unique_id()
            self.password_hash = self.encrypt_password(kwargs['raw_password'])   
            self.role = None 
            self.confirmed = False

        else:  ## existing user object from database
            self.id = kwargs['user_id']
            self.password_hash = kwargs['password_hash']
            self.role = kwargs['role'] 
            self.confirmed = kwargs['confirmed']

        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']: 
                self.role = Roles_Table[2]
            if self.role is None:
                self.role = Roles_Table[1]
        

    def generate_unique_id(self): 
        return str(uuid.uuid4())

    def encrypt_password(self, password): 
        return generate_password_hash(password) 

    def verify_password(self, password): 
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600): 
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False 
        
         ## has to be imported here to avoid circular dependencies
        from app.DynamoAccess import DynamoAccess 
        dynamo_access = DynamoAccess()
        
        user = dynamo_access.GetUserById(data.get('reset'))
        if user is None:
            return False
        user.password_hash = user.encrypt_password(new_password)
        pw_udpated = dynamo_access.UpdateUserPassword(user.id, user.password_hash)
        return pw_udpated

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps(
            {'change_email': self.id, 'new_email': new_email}).decode('utf-8')

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('change_email') != self.id:
            return False 
        
        ## has to be imported here to avoid circular dependencies
        from app.DynamoAccess import DynamoAccess 
        dynamo_access = DynamoAccess()
        
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if not dynamo_access.CheckIfEmailIsUnique(new_email):
            return False
        self.email = new_email
        return dynamo_access.UpdateUserEmail(self.id, new_email) 

    def can(self, perm):
        return self.role is not None and self.role['permission'] == perm
    
    def is_administrator(self): 
        return self.can(Permission.ADMIN)

    def to_json(self):
        json_user = {
            'url': url_for('api.get_user', id=self.id),
            'username': self.username,         
        }
        return json_user

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
         ## has to be imported here to avoid circular dependencies
        from app.DynamoAccess import DynamoAccess 
        dynamo_access = DynamoAccess()
        
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return dynamo_access.GetUserById(data['id'])

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id): 
    ## has to be imported here to avoid circular dependencies
    from app.DynamoAccess import DynamoAccess 
    dynamo_access = DynamoAccess()
    return dynamo_access.GetUserById(user_id)

    

######## Database model to keep track of active game ############
class GameDetails(db.Model):
    __tablename__ = 'gameDetails'
    id = db.Column(db.String, primary_key=True)
    game_title = db.Column(db.String) 
    match_id=db.Column(db.BigInteger,unique=True,index=True)
    game_status=db.Column(db.String) 
    squad_link=db.Column(db.String,unique=True)  
    scorecard_link=db.Column(db.String)  
    points_per_run=db.Column(db.Float) 
    points_per_wicket=db.Column(db.Float)
    game_start_time = db.Column(db.String) 
    team1 = db.Column(db.String) 
    team2 = db.Column(db.String) 
    match_result = db.Column(db.String)
    

    def __repr__(self):
        return '<GameDetails %r>' % self.match_id 