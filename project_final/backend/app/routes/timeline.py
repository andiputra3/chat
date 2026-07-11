from flask import Blueprint, request, jsonify
from app.models import db, Timeline, Notification
from app.services.telegram_service import telegram_service
from datetime import datetime

# Blueprint untuk Timeline
timeline_bp = Blueprint('timeline', __name__, url_prefix='/api/timeline')

@timeline_bp.route('/project/<project_id>', methods=['GET'])
def get_timeline(project_id):
    """Get timeline events for a project"""
    event_type = request.args.get('event_type')
    
    query = Timeline.query.filter_by(project_id=project_id)
    if event_type:
        query = query.filter_by(event_type=event_type)
    
    events = query.order_by(Timeline.created_at.desc()).all()
    return jsonify({'timeline': [e.to_dict() for e in events]})

@timeline_bp.route('', methods=['POST'])
def create_event():
    """Create timeline event"""
    data = request.get_json()
    
    required_fields = ['project_id', 'event_type', 'title']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    event = Timeline(
        project_id=data['project_id'],
        event_type=data['event_type'],
        title=data['title'],
        description=data.get('description'),
        metadata=data.get('metadata')
    )
    
    db.session.add(event)
    db.session.commit()
    
    return jsonify({'event': event.to_dict()}), 201

@timeline_bp.route('/<event_id>', methods=['DELETE'])
def delete_event(event_id):
    """Delete timeline event"""
    event = Timeline.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    
    return jsonify({'message': 'Event deleted successfully'})

# Blueprint untuk Notifications
notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')

@notifications_bp.route('', methods=['GET'])
def get_notifications():
    """Get all notifications"""
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    project_id = request.args.get('project_id')
    
    query = Notification.query
    if unread_only:
        query = query.filter_by(is_read=False)
    if project_id:
        query = query.filter_by(project_id=project_id)
    
    notifications = query.order_by(Notification.created_at.desc()).all()
    return jsonify({'notifications': [n.to_dict() for n in notifications]})

@notifications_bp.route('', methods=['POST'])
def create_notification():
    """Create notification and send to Telegram if configured"""
    data = request.get_json()
    
    required_fields = ['type', 'title', 'message']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    notification = Notification(
        type=data['type'],
        title=data['title'],
        message=data['message'],
        project_id=data.get('project_id')
    )
    
    db.session.add(notification)
    db.session.commit()
    
    # Send to Telegram if configured and enabled
    send_telegram = data.get('send_telegram', False)
    if send_telegram:
        telegram_message = f"🔔 <b>{data['title']}</b>\n\n{data['message']}"
        telegram_result = telegram_service.send_message(telegram_message)
        notification.telegram_sent = telegram_result.get('success', False)
        notification.telegram_message_id = telegram_result.get('message_id')
        db.session.commit()
    
    return jsonify({'notification': notification.to_dict()}), 201

@notifications_bp.route('/<notification_id>/read', methods=['PUT'])
def mark_as_read(notification_id):
    """Mark notification as read"""
    notification = Notification.query.get_or_404(notification_id)
    notification.is_read = True
    db.session.commit()
    
    return jsonify({'notification': notification.to_dict()})

@notifications_bp.route('/read-all', methods=['PUT'])
def mark_all_as_read():
    """Mark all notifications as read"""
    project_id = request.args.get('project_id')
    
    query = Notification.query.filter_by(is_read=False)
    if project_id:
        query = query.filter_by(project_id=project_id)
    
    notifications = query.all()
    for notification in notifications:
        notification.is_read = True
    
    db.session.commit()
    
    return jsonify({'message': 'All notifications marked as read', 'count': len(notifications)})


# Telegram Test Routes
@notifications_bp.route('/telegram/test', methods=['GET'])
def test_telegram():
    """Test Telegram connection"""
    result = telegram_service.test_connection()
    
    if result.get('success'):
        return jsonify({
            'status': 'success',
            'message': result.get('message'),
            'bot_username': result.get('bot_username'),
            'bot_name': result.get('bot_name'),
            'configured': telegram_service.is_configured()
        })
    else:
        return jsonify({
            'status': 'error',
            'error': result.get('error'),
            'configured': telegram_service.is_configured()
        }), 400


@notifications_bp.route('/telegram/send-test', methods=['POST'])
def send_test_telegram():
    """Send test message to Telegram"""
    data = request.get_json() or {}
    test_message = data.get('message', '🧪 *Test Notification*\n\nIni adalah pesan test dari AI Project Manager OS.\n\nJika Anda menerima pesan ini, konfigurasi Telegram berhasil!')
    
    result = telegram_service.send_message(test_message)
    
    if result.get('success'):
        return jsonify({
            'status': 'success',
            'message': 'Test message sent successfully!',
            'message_id': result.get('message_id'),
            'configured': telegram_service.is_configured()
        })
    else:
        return jsonify({
            'status': 'error',
            'error': result.get('error'),
            'configured': telegram_service.is_configured()
        }), 400


@notifications_bp.route('/telegram/updates', methods=['GET'])
def get_telegram_updates():
    """Get recent Telegram updates (useful for finding chat_id)"""
    limit = request.args.get('limit', 10, type=int)
    result = telegram_service.get_updates(limit=limit)
    
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


@notifications_bp.route('/telegram/config', methods=['GET'])
def get_telegram_config():
    """Get current Telegram configuration status"""
    return jsonify({
        'configured': telegram_service.is_configured(),
        'bot_token_set': bool(telegram_service.bot_token),
        'chat_id_set': bool(telegram_service.chat_id),
        'bot_token_preview': f"{telegram_service.bot_token[:10]}..." if telegram_service.bot_token else None,
        'chat_id': telegram_service.chat_id if telegram_service.chat_id else None
    })
