from flask import Blueprint, request, jsonify
from app.models import db, WorkspaceMemory
from datetime import datetime
import json

# Blueprint untuk Workspace Memory
memory_bp = Blueprint('memory', __name__, url_prefix='/api/memory')

@memory_bp.route('', methods=['GET'])
def get_memory():
    """Get workspace memory items"""
    project_id = request.args.get('project_id')
    category = request.args.get('category')
    
    if not project_id:
        return jsonify({'error': 'project_id is required'}), 400
    
    query = WorkspaceMemory.query.filter_by(project_id=project_id)
    if category:
        query = query.filter_by(category=category)
    
    items = query.order_by(WorkspaceMemory.created_at.desc()).all()
    return jsonify({'memory': [m.to_dict() for m in items]})

@memory_bp.route('', methods=['POST'])
def create_memory():
    """Create workspace memory item"""
    data = request.get_json()
    
    required_fields = ['project_id', 'category', 'title', 'content']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    memory = WorkspaceMemory(
        project_id=data['project_id'],
        category=data['category'],
        title=data['title'],
        content=data['content'],
        tags=json.dumps(data.get('tags', [])) if data.get('tags') else None,
        is_snapshot=data.get('is_snapshot', False),
        version=data.get('version', 1)
    )
    
    db.session.add(memory)
    db.session.commit()
    
    return jsonify({'memory': memory.to_dict()}), 201

@memory_bp.route('/<memory_id>', methods=['PUT'])
def update_memory(memory_id):
    """Update workspace memory item"""
    memory = WorkspaceMemory.query.get_or_404(memory_id)
    data = request.get_json()
    
    if 'title' in data:
        memory.title = data['title']
    if 'content' in data:
        memory.content = data['content']
    if 'tags' in data:
        memory.tags = json.dumps(data['tags'])
    if 'is_snapshot' in data:
        memory.is_snapshot = data['is_snapshot']
    if 'version' in data:
        memory.version = data['version']
    
    memory.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'memory': memory.to_dict()})

@memory_bp.route('/<memory_id>', methods=['DELETE'])
def delete_memory(memory_id):
    """Delete workspace memory item"""
    memory = WorkspaceMemory.query.get_or_404(memory_id)
    db.session.delete(memory)
    db.session.commit()
    
    return jsonify({'message': 'Memory item deleted successfully'})

@memory_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all available categories"""
    categories = [
        {'id': 'decisions', 'name': 'Decisions'},
        {'id': 'architecture', 'name': 'Architecture Decisions'},
        {'id': 'requirements', 'name': 'Requirements'},
        {'id': 'constraints', 'name': 'Constraints'},
        {'id': 'references', 'name': 'References'},
        {'id': 'research', 'name': 'Research'},
        {'id': 'benchmark', 'name': 'Benchmark Results'},
        {'id': 'notes', 'name': 'Notes'},
        {'id': 'scratchpad', 'name': 'Scratchpad'},
        {'id': 'todo', 'name': 'TODO'},
        {'id': 'questions', 'name': 'Questions'},
        {'id': 'lessons', 'name': 'Lessons Learned'}
    ]
    return jsonify({'categories': categories})
