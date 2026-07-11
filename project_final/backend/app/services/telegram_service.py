"""
Telegram Notification Service
Mengirim notifikasi ke Telegram Bot API
"""
import requests
import logging
from config import Config

logger = logging.getLogger(__name__)


class TelegramService:
    """Service untuk mengirim notifikasi ke Telegram"""
    
    def __init__(self):
        self.bot_token = Config.TELEGRAM_BOT_TOKEN
        self.chat_id = Config.TELEGRAM_CHAT_ID
        self.base_url = "https://api.telegram.org/bot"
    
    def is_configured(self):
        """Cek apakah Telegram sudah dikonfigurasi"""
        return bool(self.bot_token and self.chat_id)
    
    def send_message(self, message, parse_mode='HTML'):
        """
        Kirim pesan ke Telegram
        
        Args:
            message (str): Pesan yang akan dikirim
            parse_mode (str): Mode parsing (HTML, Markdown, etc.)
        
        Returns:
            dict: Response dari Telegram API
        """
        if not self.is_configured():
            logger.warning("Telegram not configured. Skipping notification.")
            return {
                'success': False,
                'error': 'Telegram bot token or chat ID not configured'
            }
        
        url = f"{self.base_url}{self.bot_token}/sendMessage"
        
        payload = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': parse_mode
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            result = response.json()
            
            if result.get('ok'):
                logger.info(f"Telegram notification sent successfully: {message[:50]}...")
                return {
                    'success': True,
                    'message_id': result.get('result', {}).get('message_id'),
                    'response': result
                }
            else:
                logger.error(f"Telegram API error: {result}")
                return {
                    'success': False,
                    'error': result.get('description', 'Unknown error'),
                    'response': result
                }
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Telegram notification: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_photo(self, photo_path, caption=''):
        """
        Kirim foto ke Telegram
        
        Args:
            photo_path (str): Path ke file foto
            caption (str): Caption untuk foto
        
        Returns:
            dict: Response dari Telegram API
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'Telegram bot token or chat ID not configured'
            }
        
        url = f"{self.base_url}{self.bot_token}/sendPhoto"
        
        try:
            with open(photo_path, 'rb') as photo:
                files = {'photo': photo}
                data = {
                    'chat_id': self.chat_id,
                    'caption': caption
                }
                
                response = requests.post(url, files=files, data=data, timeout=10)
                result = response.json()
                
                if result.get('ok'):
                    return {
                        'success': True,
                        'message_id': result.get('result', {}).get('message_id'),
                        'response': result
                    }
                else:
                    return {
                        'success': False,
                        'error': result.get('description', 'Unknown error'),
                        'response': result
                    }
        
        except Exception as e:
            logger.error(f"Failed to send Telegram photo: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_connection(self):
        """
        Test koneksi ke Telegram API
        
        Returns:
            dict: Hasil test koneksi
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'Telegram bot token or chat ID not configured'
            }
        
        # Test dengan getMe
        url = f"{self.base_url}{self.bot_token}/getMe"
        
        try:
            response = requests.get(url, timeout=10)
            result = response.json()
            
            if result.get('ok'):
                bot_info = result.get('result', {})
                return {
                    'success': True,
                    'bot_username': bot_info.get('username'),
                    'bot_name': bot_info.get('first_name'),
                    'message': f"Connected to bot @{bot_info.get('username')}"
                }
            else:
                return {
                    'success': False,
                    'error': result.get('description', 'Unknown error')
                }
        
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_updates(self, offset=None, limit=100):
        """
        Get updates dari Telegram (untuk mendapatkan chat_id jika belum tahu)
        
        Args:
            offset (int): Offset untuk polling
            limit (int): Jumlah maksimal updates
        
        Returns:
            list: List of updates
        """
        if not self.bot_token:
            return {
                'success': False,
                'error': 'Telegram bot token not configured'
            }
        
        url = f"{self.base_url}{self.bot_token}/getUpdates"
        params = {'limit': limit}
        
        if offset is not None:
            params['offset'] = offset
        
        try:
            response = requests.get(url, params=params, timeout=10)
            result = response.json()
            
            if result.get('ok'):
                return {
                    'success': True,
                    'updates': result.get('result', [])
                }
            else:
                return {
                    'success': False,
                    'error': result.get('description', 'Unknown error')
                }
        
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }


# Singleton instance
telegram_service = TelegramService()
