from flask import Blueprint, request, jsonify
from app.models import db, Build, Project, Timeline
from datetime import datetime
import os
import json

# Blueprint untuk Builder (Layer 3)
builder_bp = Blueprint('builder', __name__, url_prefix='/api/builder')

@builder_bp.route('/projects', methods=['GET'])
def get_buildable_projects():
    """Get projects that are ready for build (have FINAL_SPEC and frozen)"""
    projects = Project.query.filter_by(layer2_status='frozen', status='active').all()
    
    result = []
    for project in projects:
        # Check if FINAL_SPEC exists
        final_spec_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'workspace', project.id, 'FINAL_SPEC.md')
        has_final_spec = os.path.exists(final_spec_path)
        
        # Get latest build
        latest_build = Build.query.filter_by(project_id=project.id).order_by(Build.created_at.desc()).first()
        
        result.append({
            'project': project.to_dict(),
            'ready_to_build': has_final_spec,
            'latest_build': latest_build.to_dict() if latest_build else None
        })
    
    return jsonify({'projects': result})

@builder_bp.route('/build', methods=['POST'])
def create_build():
    """Create new build job"""
    data = request.get_json()
    
    if not data or 'project_id' not in data:
        return jsonify({'error': 'project_id is required'}), 400
    
    project = Project.query.get_or_404(data['project_id'])
    
    # Check if project is ready
    final_spec_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'workspace', project.id, 'FINAL_SPEC.md')
    if not os.path.exists(final_spec_path):
        return jsonify({'error': 'FINAL_SPEC.md not found. Project is not ready for build.'}), 400
    
    if project.layer2_status != 'frozen':
        return jsonify({'error': 'Project is not frozen. Please complete Layer 2 first.'}), 400
    
    # Create build record
    build = Build(
        project_id=project.id,
        build_number=Build.query.filter_by(project_id=project.id).count() + 1,
        status='planning',
        ai_provider=data.get('ai_provider', 'opencode'),
        model=data.get('model', 'opencode/deepseek-v4-flash-free'),
        agent=data.get('agent', 'build')
    )
    
    db.session.add(build)
    
    # Update project status
    project.layer3_status = 'planning'
    db.session.commit()
    
    # Add timeline event
    timeline = Timeline(
        project_id=project.id,
        event_type='build',
        title='Build Started',
        description=f'Build #{build.build_number} started using {build.ai_provider}/{build.model}',
        metadata=json.dumps({'build_id': build.id, 'model': build.model})
    )
    db.session.add(timeline)
    db.session.commit()
    
    return jsonify({'build': build.to_dict()}), 201

@builder_bp.route('/build/<build_id>', methods=['GET'])
def get_build(build_id):
    """Get build details"""
    build = Build.query.get_or_404(build_id)
    return jsonify({'build': build.to_dict()})

@builder_bp.route('/build/<build_id>', methods=['PUT'])
def update_build(build_id):
    """Update build status"""
    build = Build.query.get_or_404(build_id)
    data = request.get_json()
    
    if 'status' in data:
        build.status = data['status']
        
        # Update project status based on build status
        project = Project.query.get(build.project_id)
        if project:
            if data['status'] == 'building':
                project.layer3_status = 'building'
            elif data['status'] == 'testing':
                project.layer3_status = 'testing'
            elif data['status'] == 'completed':
                project.layer3_status = 'completed'
            elif data['status'] == 'failed':
                project.layer3_status = 'failed'
    
    if 'files_generated' in data:
        build.files_generated = data['files_generated']
    if 'lines_generated' in data:
        build.lines_generated = data['lines_generated']
    if 'duration_seconds' in data:
        build.duration_seconds = data['duration_seconds']
    if 'error_message' in data:
        build.error_message = data['error_message']
    if 'report_path' in data:
        build.report_path = data['report_path']
    if 'source_path' in data:
        build.source_path = data['source_path']
    
    if build.status == 'building' and not build.started_at:
        build.started_at = datetime.utcnow()
    
    if build.status in ['completed', 'failed'] and not build.completed_at:
        build.completed_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'build': build.to_dict()})

@builder_bp.route('/build/<build_id>', methods=['DELETE'])
def delete_build(build_id):
    """Delete build record"""
    build = Build.query.get_or_404(build_id)
    db.session.delete(build)
    db.session.commit()
    
    return jsonify({'message': 'Build record deleted successfully'})

@builder_bp.route('/project/<project_id>/history', methods=['GET'])
def get_build_history(project_id):
    """Get build history for a project"""
    builds = Build.query.filter_by(project_id=project_id).order_by(Build.created_at.desc()).all()
    return jsonify({'builds': [b.to_dict() for b in builds]})
