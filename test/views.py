# -*-encoding=UTF-8 -*-
from _init_ import app, db
from flask import render_template
from flask import render_template, redirect, request, flash, get_flashed_messages, send_from_directory
from models import *
import random, hashlib, uuid, os
import jinja2, json
from flask_login import login_user, logout_user, current_user, login_required
from qiniu import Auth, put_file, etag, urlsafe_base64_encode
import qiniu.config
from qiniusdk import qiniu_upload_file


def redirect_with_msg(target, msg, category):
    if msg != None:
        flash(msg, category=category)
    return redirect(target)


@app.route('/')
def index():
    #  return 'hello'
    images = Image.query.order_by(db.desc(Image.create_data)).limit(5).all()
    # users = User.query.order_by(db.desc(User.id)).limit(5).all()

    # 此处的images=images 为**kv  为默认参数指代,可传入0或任意多个参数
    return render_template('index.html', images=images)


@app.route('/image/<int:image_id>/')
def image(image_id):
    image = Image.query.get(image_id)
    if image == None:
        return redirect('/')
    return render_template('pageDetail.html', image=image)


@app.route('/profile/<int:user_id>/')
@login_required
def profile(user_id):
    print(current_user.username, type(current_user.id))
    user = User.query.get(user_id)
    if user == None:
        # redirect ==重定向
        return redirect('/')
    paginate = Image.query.filter_by(user_id=user_id).paginate(page=1, per_page=3)
    return render_template('profile.html', user=user, images=paginate.items, has_next=paginate.has_next)


@app.route('/profile/images/<int:user_id>/<int:page>/<int:per_page>/')
def user_images(user_id, page, per_page):
    # 参数检查
    paginate = Image.query.filter_by(user_id=user_id).paginate(page=page, per_page=per_page)

    map = {'has_next': paginate.has_next}
    images = []
    # map  k-v 教程
    for image in paginate.items:
        imgvo = {'id': image.id, 'url': image.url, 'comment_count': len(image.comments)}
        images.append(imgvo)
    map['images'] = images
    return json.dumps(map)


# 登录页面
@app.route('/login/')
def login():
    if current_user.is_authenticated:
        return redirect('/')
    msg = ''
    for m in get_flashed_messages(with_categories=False, category_filter=['reg']):
        msg = msg + m
    return render_template('login.html', msg=msg, next=request.values.get('next'))


# 注册按钮
@app.route('/reg/', methods=['get', 'post'])
def reg():
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()
    if username == '' or password == '':
        return redirect_with_msg(u'/login/', '账号或密码为空', category='reg')
    # flask  http://docs.jinkan.org/docs/flask/patterns/flashing.html
    user = User.query.filter_by(username=username).first()
    if user != None:
        return redirect_with_msg(u'/login/', '用户已存在', category='reg')
    salt = '.'.join(random.sample('0123456789asdzxcvmbnfeASDNVIKF', 10))
    m = hashlib.md5()
    m.update((password + salt).encode("utf8"))
    password = m.hexdigest()
    user = User(username, password, salt=salt)
    db.session.add(user)
    db.session.commit()

    login_user(user)

    next = user.id
    if next != None:
        return redirect('/profile/' + str(next) + '/')

    return redirect('/')


# 登录按钮
@app.route('/true_login/', methods=['get', 'post'])
def true_login():
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()
    user = User.query.filter_by(username=username).first()
    if username == '' or password == '':
        return redirect_with_msg('/login/', u'用户名和密码不能为空', 'reglogin')

    user = User.query.filter_by(username=username).first()
    if user == None:
        return redirect_with_msg('/login/', u'用户名不存在', 'reglogin')

    m = hashlib.md5()
    m.update((password + user.salt).encode("utf8"))
    if m.hexdigest() != user.password:
        return redirect_with_msg('/login/', u'密码错误', 'reglogin')

    login_user(user)

    next = user.id
    if next != None:
        return redirect('/profile/' + str(next) + '/')

    return redirect('/')


# 注销按钮
@app.route('/logout/')
def logout():
    logout_user()
    return redirect('/')


def save_to_local(file, file_name):
    save_dir = app.config['UPLOAD_DIR']
    file.save(os.path.join(save_dir, file_name))
    return str('/image/' + file_name)
    #return  None


@app.route('/upload/', methods=['post'])
def upload():
    # k-v
    # print(current_user,current_user.id,type(current_user.id))
    file = request.files['file']
    file_ext = ''
    if file.filename.find('.') > 0:
        file_ext = file.filename.rsplit('.', 1)[1].strip().lower()
    if file_ext in app.config['ALLOWED_EXT']:
        file_name = str(uuid.uuid1()).replace('-', '') + '.' + file_ext
        #url=save_to_local(file, file_name)
        url = qiniu_upload_file(file, file_name)
        if url != None:
            db.session.add(Image(url, int(current_user.id)))
            db.session.commit()
    # return redirect('/')
    return redirect('/profile/%d' % int(current_user.id))


@app.route('/image/<image_name>')
def view_image(image_name):
    return send_from_directory(app.config['UPLOAD_DIR'], image_name)
