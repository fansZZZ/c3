# -*-encoding=UTF-8 -*-
from _init_ import db, login_manager
from _datetime import datetime
import random


class Comment(db.Model):
    # 加上这句话数据库才能识别中文
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.String(1024))
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.Integer, default=0)  # 0 正常 1删除
    user = db.relationship('User')

    def __init__(self, content, image_id, user_id):
        self.content = content
        self.image_id = image_id
        self.user_id = user_id

    def __repr__(self):
        return ('<Comment%d %s>' % (self.id, self.content)).encode('gbk')


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url = db.Column(db.String(1024))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    create_data = db.Column(db.DateTime)
    comments = db.relationship('Comment')

    # user = db.relationship('User',backref='user', lazy='dynamic')

    def __init__(self, url, user_id):
        self.url = url
        self.user_id = user_id
        self.create_data = datetime.now()

    def __repr__(self):
        return '<Image %d %s>' % (self.id, self.url)


class User(db.Model):
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(32))
    salt = db.Column(db.String(32))
    head_url = db.Column(db.String(256))
    # User类必须连接到Image表中，两个表中的外键和主键对应约束（两个表中的外键），
    # backref：反向引用， 正向：user.images  反向image.user
    images = db.relationship('Image', backref='user', lazy='dynamic')

    def __init__(self, username, password, salt=''):
        self.username = username
        self.password = password
        self.salt = salt
        self.head_url = 'http://images.nowcoder.com/head/' + str(random.randint(0, 1000)) + 't.png'

    def __repr__(self):
        return '<User %r>' % self.username


    # Flask Login接口

    def is_authenticated(self):
        print('is_authenticated')
        return True


    def is_active(self):
        print('is_active')
        return True


    def is_anonymous(self):
        print('is_anonymous')
        return False


    def get_id(self):
        print('get_id')
        return self.id


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

