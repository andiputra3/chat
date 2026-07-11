from flask import Blueprint, request, jsonify
from app.models import db, Project, Chat, Message, WorkspaceMemory, FactoryJob, Build, Timeline, Notification
from datetime import datetime
import os
import json

# Blueprint untuk Project Management
projects_bp = Blueprint('projects', __name__, url_prefix='/api/projects')

@projects_bp.route('', methods=['GET'])
def get_projects():
    """Get all projects"""
    projects = Project.query.all()
    return jsonify({'projects': [p.to_dict() for p in projects]})

@projects_bp.route('', methods=['POST'])
def create_project():
    """Create new project"""
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({'error': 'Project name is required'}), 400
    
    project = Project(
        name=data['name'],
        description=data.get('description', ''),
        version=data.get('version', '1.0.0')
    )
    
    db.session.add(project)
    db.session.commit()
    
    # Create workspace directory for project
    workspace_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'workspace', project.id)
    os.makedirs(workspace_dir, exist_ok=True)
    
    # Add timeline event
    timeline = Timeline(
        project_id=project.id,
        event_type='system',
        title='Project Created',
        description=f'Project {project.name} was created',
        metadata=json.dumps({'version': project.version})
    )
    db.session.add(timeline)
    db.session.commit()
    
    return jsonify({'project': project.to_dict()}), 201

@projects_bp.route('/<project_id>', methods=['GET'])
def get_project(project_id):
    """Get project by ID"""
    project = Project.query.get_or_404(project_id)
    return jsonify({'project': project.to_dict()})

@projects_bp.route('/<project_id>', methods=['PUT'])
def update_project(project_id):
    """Update project"""
    project = Project.query.get_or_404(project_id)
    data = request.get_json()
    
    if 'name' in data:
        project.name = data['name']
    if 'description' in data:
        project.description = data['description']
    if 'version' in data:
        project.version = data['version']
    if 'status' in data:
        project.status = data['status']
    if 'layer2_status' in data:
        project.layer2_status = data['layer2_status']
    if 'layer3_status' in data:
        project.layer3_status = data['layer3_status']
    
    project.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'project': project.to_dict()})

@projects_bp.route('/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    """Delete project (soft delete)"""
    project = Project.query.get_or_404(project_id)
    project.status = 'deleted'
    project.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Project deleted successfully'})

@projects_bp.route('/<project_id>/status', methods=['GET'])
def get_project_status(project_id):
    """Get detailed project status including Layer 2 and Layer 3 readiness"""
    project = Project.query.get_or_404(project_id)
    
    # Check if FINAL_SPEC exists
    final_spec_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'workspace', project.id, 'FINAL_SPEC.md')
    has_final_spec = os.path.exists(final_spec_path)
    
    # Get latest factory job
    latest_job = FactoryJob.query.filter_by(project_id=project_id).order_by(FactoryJob.created_at.desc()).first()
    
    # Get latest build
    latest_build = Build.query.filter_by(project_id=project_id).order_by(Build.created_at.desc()).first()
    
    status = {
        'project': project.to_dict(),
        'layer2_ready': project.layer2_status == 'frozen' and has_final_spec,
        'layer3_ready': project.layer2_status == 'frozen' and has_final_spec,
        'has_final_spec': has_final_spec,
        'latest_factory_job': latest_job.to_dict() if latest_job else None,
        'latest_build': latest_build.to_dict() if latest_build else None
    }
    
    return jsonify(status)
