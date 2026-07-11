from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
import os
import sys

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models import db

# Import blueprints
from app.routes.projects import projects_bp
from app.routes.chats import chats_bp
from app.routes.memory import memory_bp
from app.routes.factory import factory_bp
from app.routes.builder import builder_bp
from app.routes.timeline import timeline_bp, notifications_bp
from app.routes.telegram_config import telegram_config_bp

def create_app(config_class=Config):
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    CORS(app)
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(projects_bp)
    app.register_blueprint(chats_bp)
    app.register_blueprint(memory_bp)
    app.register_blueprint(factory_bp)
    app.register_blueprint(builder_bp)
    app.register_blueprint(timeline_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(telegram_config_bp)
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'AI Project Manager OS Backend is running'
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create workspace directory
        os.makedirs(Config.WORKSPACE_DIR, exist_ok=True)
        os.makedirs(Config.DOCS_DIR, exist_ok=True)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
