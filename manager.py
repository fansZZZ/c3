# -*-encoding=UTF-8 -*-
import sys
import os
import unittest

sys.path.append(os.getcwd() + '/test')
from _init_ import app
from _init_ import db
from flask_script import Manager
from models import *
from flask import request
import test

manager = Manager(app)


def get_image_url():
    return 'http://images.nowcoder.com/head/' + str(random.randint(0, 1000)) + 'm.png'


# python manager.py init_database
@manager.command
def init_database():
    db.drop_all()
    db.create_all()
    for i in range(0, 100):
        db.session.add(User('User' + str(i), 'a' + str(i)))
        for j in range(0, 10):
            db.session.add(Image(get_image_url(), str(i + 1)))
            for k in range(0, 3):
                db.session.add(Comment('这是一条评论' + str(k), 1 + 3 * i + j, i + 1))
    db.session.commit()

    # print(4,Image.query.order_by(db.desc(Image.create_data)).limit(5).all())
    # print(db.session.query(User.id).all())


@manager.command
def run_test():
    db.drop_all()
    db.create_all()
    tests = unittest.TestLoader().discover('./')
    unittest.TextTestRunner().run(tests)
    pass


if __name__ == '__main__':
    manager.run()
