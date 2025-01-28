class Config:
    # 基本配置
    SECRET_KEY = 'your-secret-key-here'
    DEBUG = True
    
    # 服务器配置
    HOST = '0.0.0.0'
    PORT = 5000
    
    # 数据库配置
    DATABASE_PATH = 'data/chat_history.db'
    
    # 用户名配置
    NAMES_FILE_PATH = 'data/names.txt'
    
    # 上传配置
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size 