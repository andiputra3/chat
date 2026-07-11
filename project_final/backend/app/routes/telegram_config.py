"""
Route untuk konfigurasi Telegram yang dapat diubah secara dinamis
"""
from flask import Blueprint, request, jsonify
import os
import json

telegram_config_bp = Blueprint('telegram_config', __name__, url_prefix='/api/telegram')

# File untuk menyimpan konfigurasi Telegram
CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'telegram_config.json')


def load_telegram_config():
    """Load konfigurasi Telegram dari file JSON"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {'bot_token': '', 'chat_id': ''}


def save_telegram_config(bot_token, chat_id):
    """Simpan konfigurasi Telegram ke file JSON"""
    # Pastikan direktori instance ada
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    
    config = {
        'bot_token': bot_token,
        'chat_id': chat_id
    }
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    
    return config


@telegram_config_bp.route('/config', methods=['GET'])
def get_config():
    """Dapatkan konfigurasi Telegram saat ini"""
    config = load_telegram_config()
    
    return jsonify({
        'configured': bool(config['bot_token'] and config['chat_id']),
        'bot_token_set': bool(config['bot_token']),
        'chat_id_set': bool(config['chat_id']),
        'bot_token_preview': f"{config['bot_token'][:10]}..." if config['bot_token'] else None,
        'chat_id': config['chat_id'] if config['chat_id'] else None
    })


@telegram_config_bp.route('/config', methods=['POST'])
def set_config():
    """Simpan konfigurasi Telegram"""
    data = request.get_json()
    
    if not data:
        return jsonify({'status': 'error', 'error': 'No data provided'}), 400
    
    bot_token = data.get('bot_token', '').strip()
    chat_id = data.get('chat_id', '').strip()
    
    if not bot_token or not chat_id:
        return jsonify({
            'status': 'error',
            'error': 'Both bot_token and chat_id are required'
        }), 400
    
    # Simpan konfigurasi
    config = save_telegram_config(bot_token, chat_id)
    
    # Update environment variables untuk session ini
    os.environ['TELEGRAM_BOT_TOKEN'] = bot_token
    os.environ['TELEGRAM_CHAT_ID'] = chat_id
    
    return jsonify({
        'status': 'success',
        'message': 'Configuration saved successfully',
        'configured': True
    })


@telegram_config_bp.route('/test', methods=['GET'])
def test_connection():
    """Test koneksi ke Telegram API"""
    from app.services.telegram_service import telegram_service
    
    # Reload konfigurasi dari file
    config = load_telegram_config()
    if config['bot_token']:
        os.environ['TELEGRAM_BOT_TOKEN'] = config['bot_token']
    if config['chat_id']:
        os.environ['TELEGRAM_CHAT_ID'] = config['chat_id']
    
    # Buat instance baru dengan konfigurasi terbaru
    from app.services.telegram_service import TelegramService
    service = TelegramService()
    
    result = service.test_connection()
    
    if result.get('success'):
        return jsonify({
            'status': 'success',
            'message': result.get('message'),
            'bot_username': result.get('bot_username'),
            'bot_name': result.get('bot_name'),
            'configured': service.is_configured()
        })
    else:
        return jsonify({
            'status': 'error',
            'error': result.get('error'),
            'configured': service.is_configured()
        }), 400


@telegram_config_bp.route('/send-test', methods=['POST'])
def send_test_message():
    """Kirim pesan test ke Telegram"""
    from app.services.telegram_service import TelegramService
    
    # Reload konfigurasi dari file
    config = load_telegram_config()
    if config['bot_token']:
        os.environ['TELEGRAM_BOT_TOKEN'] = config['bot_token']
    if config['chat_id']:
        os.environ['TELEGRAM_CHAT_ID'] = config['chat_id']
    
    data = request.get_json() or {}
    message = data.get('message', '🧪 *Test Notification*\n\nIni adalah pesan test dari AI Project Manager OS.\n\nJika Anda menerima pesan ini, konfigurasi Telegram berhasil!')
    
    # Buat instance baru dengan konfigurasi terbaru
    service = TelegramService()
    result = service.send_message(message)
    
    if result.get('success'):
        return jsonify({
            'status': 'success',
            'message': 'Test message sent successfully!',
            'message_id': result.get('message_id'),
            'configured': service.is_configured()
        })
    else:
        return jsonify({
            'status': 'error',
            'error': result.get('error'),
            'configured': service.is_configured()
        }), 400


@telegram_config_bp.route('/updates', methods=['GET'])
def get_updates():
    """Dapatkan updates dari Telegram (untuk menemukan chat_id)"""
    from app.services.telegram_service import TelegramService
    
    # Reload konfigurasi dari file
    config = load_telegram_config()
    if config['bot_token']:
        os.environ['TELEGRAM_BOT_TOKEN'] = config['bot_token']
    
    limit = request.args.get('limit', 10, type=int)
    
    # Buat instance baru dengan konfigurasi terbaru
    service = TelegramService()
    result = service.get_updates(limit=limit)
    
    if result.get('success'):
        return jsonify({
            'status': 'success',
            'updates': result.get('updates', [])
        })
    else:
        return jsonify({
            'status': 'error',
            'error': result.get('error')
        }), 400
