import sys
import os

sys.path.append(os.getcwd() + '/test')
import unittest
from _init_ import app


class c3Test(unittest.TestCase):
    def setUp(self):
        print('setup')
        app.config['TESTING']=True
        self.app=app.test_client()


    def tearDown(self):
        print('tearDown')

    def register(self,username,password):
        return self.app.post('/reg/',data={'username':username,'password':password},follow_redirects=True)

    def login(self, username, password):
        return self.app.post('/true_login/', data={"username": username, "password": password}, follow_redirects=True)

    def logout(self):
        return self.app.get('/logout/')
    #assert:断言
    def test_reg_logout(self):
        assert self.register("hello","world").status_code==200


    def test2(self):
        print('test2')
