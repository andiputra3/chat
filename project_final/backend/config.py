import os
from datetime import datetime

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///project_manager.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    WORKSPACE_DIR = os.path.join(BASE_DIR, '..', 'workspace')
    DOCS_DIR = os.path.join(BASE_DIR, '..', 'docs')
    
    # AI Runtime
    DEFAULT_AI_PROVIDER = os.environ.get('AI_PROVIDER', 'opencode')
    DEFAULT_MODEL = os.environ.get('AI_MODEL', 'opencode/deepseek-v4-flash-free')
    DEFAULT_AGENT = os.environ.get('AI_AGENT', 'plan')
    DEFAULT_TIMEOUT = int(os.environ.get('AI_TIMEOUT', '600'))
    
    # Notification
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')
    
    # Factory Settings
    MAX_CONCURRENT_JOBS = int(os.environ.get('MAX_CONCURRENT_JOBS', '1'))
    ENABLE_THINKING_MODE = os.environ.get('ENABLE_THINKING_MODE', 'false').lower() == 'true'
    
    @staticmethod
    def init_app(app):
        """Initialize application"""
        # Create necessary directories
        os.makedirs(Config.WORKSPACE_DIR, exist_ok=True)
        os.makedirs(Config.DOCS_DIR, exist_ok=True)
