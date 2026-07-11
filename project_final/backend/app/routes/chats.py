from flask import Blueprint, request, jsonify
from app.models import db, Chat, Message
from datetime import datetime
import os
import json

# Blueprint untuk Chat
chats_bp = Blueprint('chats', __name__, url_prefix='/api/chats')

@chats_bp.route('', methods=['GET'])
def get_chats():
    """Get all chats for a project"""
    project_id = request.args.get('project_id')
    if not project_id:
        return jsonify({'error': 'project_id is required'}), 400
    
    chats = Chat.query.filter_by(project_id=project_id).order_by(Chat.created_at.desc()).all()
    return jsonify({'chats': [c.to_dict() for c in chats]})

@chats_bp.route('', methods=['POST'])
def create_chat():
    """Create new chat session"""
    data = request.get_json()
    
    if not data or 'project_id' not in data:
        return jsonify({'error': 'project_id is required'}), 400
    
    chat = Chat(
        project_id=data['project_id'],
        title=data.get('title', 'New Chat'),
        session_id=data.get('session_id')
    )
    
    db.session.add(chat)
    db.session.commit()
    
    return jsonify({'chat': chat.to_dict()}), 201

@chats_bp.route('/<chat_id>', methods=['GET'])
def get_chat(chat_id):
    """Get chat with messages"""
    chat = Chat.query.get_or_404(chat_id)
    
    messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.created_at.asc()).all()
    
    chat_data = chat.to_dict()
    chat_data['messages'] = [m.to_dict() for m in messages]
    
    return jsonify({'chat': chat_data})

@chats_bp.route('/<chat_id>', methods=['PUT'])
def update_chat(chat_id):
    """Update chat (pin, archive, rename)"""
    chat = Chat.query.get_or_404(chat_id)
    data = request.get_json()
    
    if 'title' in data:
        chat.title = data['title']
    if 'is_pinned' in data:
        chat.is_pinned = data['is_pinned']
    if 'is_archived' in data:
        chat.is_archived = data['is_archived']
    if 'session_id' in data:
        chat.session_id = data['session_id']
    
    chat.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'chat': chat.to_dict()})

@chats_bp.route('/<chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    """Delete chat"""
    chat = Chat.query.get_or_404(chat_id)
    db.session.delete(chat)
    db.session.commit()
    
    return jsonify({'message': 'Chat deleted successfully'})

@chats_bp.route('/<chat_id>/messages', methods=['POST'])
def add_message(chat_id):
    """Add message to chat"""
    data = request.get_json()
    
    if not data or 'role' not in data or 'content' not in data:
        return jsonify({'error': 'role and content are required'}), 400
    
    message = Message(
        chat_id=chat_id,
        role=data['role'],
        content=data['content'],
        thinking=data.get('thinking'),
        attachments=json.dumps(data.get('attachments', [])) if data.get('attachments') else None
    )
    
    db.session.add(message)
    db.session.commit()
    
    return jsonify({'message': message.to_dict()}), 201

@chats_bp.route('/<chat_id>/messages/<message_id>', methods=['DELETE'])
def delete_message(chat_id, message_id):
    """Delete specific message"""
    message = Message.query.get_or_404(message_id)
    if message.chat_id != chat_id:
        return jsonify({'error': 'Message not found in this chat'}), 404
    
    db.session.delete(message)
    db.session.commit()
    
    return jsonify({'message': 'Message deleted successfully'})
