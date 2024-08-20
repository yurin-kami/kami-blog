from flask import Flask,jsonify,request
from flask_cors import CORS
from werkzeug.utils import secure_filename
from wtforms import StringField, PasswordField
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from base_models import Kami, Music,BlogPost,BookshelfItem,User
from get_music import GetMusic
from get_light_note import Book
import json
import logging

app = Flask(__name__)
app.config['WTF_CSRF_ENABLED'] = False
CORS(app)  # 允许所有来源的请求

app.logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
app.logger.addHandler(handler)
# 或者指定允许的来源
CORS(app, resources={r"/api/*": {"origins": "*"}})
csrf_protect = CSRFProtect(app)
class LoginForm(FlaskForm):  # 确保继承自 FlaskForm
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])

@app.route('/music')
def get_music():  # put application's code here
    kami=Kami()
    data=kami.query(Music)#字典嵌入列表
    return jsonify(data)
@app.route('/blog/<string:title>')
def get_blog_by_title(title):
    kami = Kami()
    data = kami.query(BlogPost, title=title)
    return jsonify(data)
@app.route('/blogs')
def get_blogs():
    kami=Kami()
    data=kami.query(BlogPost)#字典嵌入列表
    titles=[]
    for i in data:
        titles.append(i['title'])
    print(titles)
    return titles
@app.route('/bookshelf')
def get_bookshelf():
    kami=Kami()
    data=kami.query(BookshelfItem)#字典嵌入列表
    return jsonify(data)
@app.route('/user')
def get_user():
    kami=Kami()
    data=kami.query(User)#字典嵌入列表
    return jsonify(data)
@app.route('/music/update/<id>')
def music_update(id:str):#需要歌手id
    kami=Kami()
    get_music=GetMusic()
    data=get_music.get_all_info(id)
    data=kami.insert_music(Music,data)#字典嵌入列表
    return json.dumps(data)
@app.route('/book/update')
def book_update():
    kami=Kami()
    get_book=Book()
    data=get_book.get_book()
    data=kami.insert_book(BookshelfItem,data)#字典嵌入列表
    return json.dumps(data)
@app.route('/admin', methods=['POST'])
@csrf_protect.exempt  # Disable CSRF protection for this route
def admin():
    form = LoginForm(request.form)  # 使用 request.form 初始化表单
    if form.validate_on_submit():  # 使用 validate_on_submit 方法验证表单
        # 获取用户数据
        users = Kami().query(User)
        user=users[0]
        # print(user)
        # print(form.username.data,form.password.data)
        # 验证用户名和密码
        if user['username'] == form.username.data and user['password'] == form.password.data:
            return jsonify({"message": "Login successful"})
        return jsonify({"message": "Invalid credentials"}), 401
    else:
        return jsonify({"message": "Invalid form data"}), 400
@app.route('/writeblog', methods=['POST'])
def write_blog():
    kami=Kami()
    # 从请求体中获取 JSON 数据和文件
    data = request.form.to_dict(flat=False)
    file = request.files.get('file')

    # 确认接收到的数据包含必要的字段
    if 'title' not in data or 'content' not in data or 'tags' not in data:
        return jsonify({"message": "Missing required fields"}), 400

    # 确保 tags 是一个列表
    if isinstance(data['tags'][0], str):
        data['tags']=json.loads(data['tags'][0])
    elif not isinstance(data['tags'][0], list):
        return jsonify({"message": "Tags must be a string or a list"}), 400
    # 如果有文件上传，则读取文件内容并替换 content 字段
    if file:
        filename = secure_filename(file.filename)
        file_content = file.read().decode('utf-8')
        data['content'] = file_content

    # 保存到数据库
    result = kami.insert_blog(data)

    # 根据保存结果返回响应
    if result == "ok":
        return jsonify({"message": "Blog saved successfully"}), 201
    else:
        return jsonify({"message": "Failed to save blog"}), 500

# @app.route('/csrf-token', methods=['GET'])
# def get_csrf_token():
#     csrf_token = session.get('_csrf_token', None)
#     if csrf_token is None:
#         csrf_token = generate_csrf()
#         session['_csrf_token'] = csrf_token
#     return jsonify({'csrfToken': csrf_token})


if __name__ == '__main__':
    app.run()
