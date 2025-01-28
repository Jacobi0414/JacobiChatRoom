import os
import sqlite3
from datetime import datetime
import random
import markdown
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.nl2br import Nl2BrExtension
from markdown.extensions.sane_lists import SaneListExtension
import logging
import codecs
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, jsonify, url_for
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app, cors_allowed_origins="*")

# 设置日志
if not os.path.exists('logs'):
    os.makedirs('logs')

# 自定义日志处理器，支持UTF-8编码
class UTF8RotatingFileHandler(RotatingFileHandler):
    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding='utf-8', delay=False):
        super().__init__(filename, mode, maxBytes, backupCount, encoding, delay)
    
    def emit(self, record):
        try:
            if self.stream is None:
                if self.mode != 'w' or not self.delay:
                    self.stream = codecs.open(self.baseFilename, self.mode, self.encoding)
            msg = self.format(record)
            stream = self.stream
            stream.write(msg + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)

# 设置控制台日志处理器
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
console_handler.setLevel(logging.INFO)
app.logger.addHandler(console_handler)

# 设置文件日志处理器
file_handler = UTF8RotatingFileHandler('logs/chatroom.log', maxBytes=10240000, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('聊天室启动')

# 在线用户字典
online_users = {}

# 数据库连接上下文管理器
class DatabaseConnection:
    def __init__(self, db_path):
        self.db_path = db_path

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()
        if exc_type:
            app.logger.error(f"Database error: {exc_val}")
            return False

# 错误处理
@app.errorhandler(404)
def not_found_error(error):
    app.logger.error(f'Page not found: {request.url}')
    return jsonify({'error': '页面未找到'}), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f'Server Error: {error}')
    return jsonify({'error': '服务器内部错误'}), 500

def init_db():
    """初始化数据库"""
    try:
        if not os.path.exists('data'):
            os.makedirs('data')
        
        with DatabaseConnection(app.config['DATABASE_PATH']) as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS messages
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT NOT NULL,
                 message TEXT NOT NULL,
                 timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)
            ''')
            conn.commit()
        app.logger.info('Database initialized successfully')
    except Exception as e:
        app.logger.error(f'Database initialization error: {e}')
        raise

def get_random_name():
    """从names.txt中获取随机用户名"""
    try:
        with open(app.config['NAMES_FILE_PATH'], 'r', encoding='utf-8') as f:
            names = [line.strip() for line in f if line.strip()]
        
        # 如果所有名字都被使用了，添加数字后缀
        available_names = []
        for name in names:
            if name not in online_users.values():
                available_names.append(name)
            else:
                # 尝试添加数字后缀
                for i in range(2, 100):
                    new_name = f"{name}{i}"
                    if new_name not in online_users.values():
                        available_names.append(new_name)
                        break
        
        if available_names:
            return random.choice(available_names)
        return f"访客{random.randint(1000, 9999)}"
    except Exception as e:
        app.logger.error(f"Error reading names file: {e}")
        return f"访客{random.randint(1000, 9999)}"

@app.route('/')
def index():
    """渲染主页"""
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    """处理新用户连接"""
    username = get_random_name()
    online_users[request.sid] = username
    emit('user_joined', {'username': username}, broadcast=True)
    emit('update_users', {'users': list(online_users.values())}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    """处理用户断开连接"""
    if request.sid in online_users:
        username = online_users.pop(request.sid)
        emit('user_left', {'username': username}, broadcast=True)
        emit('update_users', {'users': list(online_users.values())}, broadcast=True)

def convert_markdown(text):
    """转换Markdown文本，支持更多语法特性"""
    return markdown.markdown(text, extensions=[
        'markdown.extensions.fenced_code',  # 支持围栏代码块 ```code```
        'markdown.extensions.tables',       # 支持表格
        'markdown.extensions.nl2br',        # 支持换行
        'markdown.extensions.sane_lists',   # 更好的列表支持
        'markdown.extensions.extra',        # 包含更多扩展特性
        'markdown.extensions.codehilite',   # 代码高亮
        'markdown.extensions.toc',          # 目录生成
        'markdown.extensions.footnotes',    # 脚注支持
        'markdown.extensions.attr_list',    # 属性列表
        'markdown.extensions.def_list',     # 定义列表
        'markdown.extensions.abbr',         # 缩写支持
        'markdown.extensions.meta'          # 元数据支持
    ], output_format='html5')

@socketio.on('message')
def handle_message(data):
    """处理新消息"""
    try:
        username = online_users.get(request.sid, "未知用户")
        message = data.get('message', '')
        
        # 转换Markdown语法
        html_message = convert_markdown(message)
        
        # 保存消息到数据库
        with DatabaseConnection(app.config['DATABASE_PATH']) as conn:
            c = conn.cursor()
            c.execute('INSERT INTO messages (username, message) VALUES (?, ?)',
                   (username, message))
            conn.commit()
        
        # 广播消息给所有用户
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        emit('message', {
            'username': username,
            'message': html_message,
            'timestamp': current_time
        }, broadcast=True)
        
        # 安全地记录日志，截断过长消息并处理特殊字符
        log_message = message.encode('unicode_escape').decode('ascii')
        if len(log_message) > 50:
            log_message = log_message[:47] + '...'
        app.logger.info(f'Message sent by {username}: {log_message}')
    except Exception as e:
        app.logger.error(f'Error handling message: {str(e)}')
        emit('error', {'message': '消息发送失败'})

@app.route('/history')
def get_history():
    """获取聊天历史"""
    conn = sqlite3.connect(app.config['DATABASE_PATH'])
    c = conn.cursor()
    c.execute('SELECT username, message, timestamp FROM messages ORDER BY timestamp DESC LIMIT 50')
    messages = [{
        'username': row[0],
        'message': convert_markdown(row[1]),
        'timestamp': row[2]
    } for row in c.fetchall()]
    conn.close()
    return jsonify(messages[::-1])

def allowed_file(filename):
    """检查文件类型是否允许"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    """处理文件上传"""
    if 'file' not in request.files:
        return jsonify({'error': '没有文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # 添加时间戳防止文件名冲突
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # 返回文件URL
        file_url = url_for('static', filename=f'uploads/{filename}')
        return jsonify({'url': file_url})
    
    return jsonify({'error': '不支持的文件类型'}), 400

@socketio.on('image_message')
def handle_image_message(data):
    """处理图片消息"""
    username = online_users.get(request.sid, "未知用户")
    image_url = data.get('url', '')
    
    # 构建Markdown格式的图片消息
    message = f"![图片]({image_url})"
    
    # 保存到数据库
    conn = sqlite3.connect(app.config['DATABASE_PATH'])
    c = conn.cursor()
    c.execute('INSERT INTO messages (username, message) VALUES (?, ?)',
              (username, message))
    conn.commit()
    conn.close()
    
    # 广播消息
    emit('message', {
        'username': username,
        'message': markdown.markdown(message),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }, broadcast=True)

@socketio.on_error()
def error_handler(e):
    """处理WebSocket错误"""
    app.logger.error(f'WebSocket error: {str(e)}')
    emit('error', {'message': '发生错误，请刷新页面重试'})

@socketio.on_error_default
def default_error_handler(e):
    """默认WebSocket错误处理"""
    app.logger.error(f'WebSocket default error: {str(e)}')
    emit('error', {'message': '发生未知错误'})

if __name__ == '__main__':
    init_db()
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    socketio.run(app,
                host=app.config['HOST'],
                port=app.config['PORT'],
                debug=app.config['DEBUG'])
