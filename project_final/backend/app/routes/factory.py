from flask import Blueprint, request, jsonify
from app.models import db, FactoryJob, Project, Timeline
from datetime import datetime
import os
import json
import uuid

# Blueprint untuk Factory (Layer 2)
factory_bp = Blueprint('factory', __name__, url_prefix='/api/factory')

@factory_bp.route('/queue', methods=['GET'])
def get_factory_queue():
    """Get factory queue with WIB timestamps"""
    jobs = FactoryJob.query.order_by(FactoryJob.created_at.desc()).all()
    return jsonify({'queue': [j.to_dict() for j in jobs]})

@factory_bp.route('/job', methods=['POST'])
def create_factory_job():
    """Create new factory job"""
    data = request.get_json()
    
    if not data or 'project_id' not in data:
        return jsonify({'error': 'project_id is required'}), 400
    
    project = Project.query.get_or_404(data['project_id'])
    
    # Generate queue ID
    queue_number = FactoryJob.query.count() + 1
    queue_id = f"Q-{queue_number:04d}"
    
    job = FactoryJob(
        queue_id=queue_id,
        project_id=data['project_id'],
        stage=data.get('stage', 'input'),
        status='waiting'
    )
    
    db.session.add(job)
    
    # Update project status
    project.layer2_status = 'in_progress'
    db.session.commit()
    
    # Add timeline event
    timeline = Timeline(
        project_id=project.id,
        event_type='factory',
        title='Factory Job Started',
        description=f'Factory job {queue_id} started at stage {job.stage}',
        metadata=json.dumps({'queue_id': queue_id, 'stage': job.stage})
    )
    db.session.add(timeline)
    db.session.commit()
    
    return jsonify({'job': job.to_dict()}), 201

@factory_bp.route('/job/<job_id>', methods=['GET'])
def get_factory_job(job_id):
    """Get factory job details"""
    job = FactoryJob.query.get_or_404(job_id)
    return jsonify({'job': job.to_dict()})

@factory_bp.route('/job/<job_id>', methods=['PUT'])
def update_factory_job(job_id):
    """Update factory job status and progress"""
    job = FactoryJob.query.get_or_404(job_id)
    data = request.get_json()
    
    if 'stage' in data:
        job.stage = data['stage']
    if 'status' in data:
        job.status = data['status']
    if 'progress' in data:
        job.progress = data['progress']
    if 'error_message' in data:
        job.error_message = data['error_message']
    if 'output_path' in data:
        job.output_path = data['output_path']
    
    if job.status == 'running' and not job.started_at:
        job.started_at = datetime.utcnow()
    
    if job.status in ['completed', 'failed'] and not job.completed_at:
        job.completed_at = datetime.utcnow()
        
        # Update project status if completed
        if job.status == 'completed' and job.stage == 'freeze':
            project = Project.query.get(job.project_id)
            if project:
                project.layer2_status = 'frozen'
    
    job.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'job': job.to_dict()})

@factory_bp.route('/job/<job_id>', methods=['DELETE'])
def delete_factory_job(job_id):
    """Delete factory job"""
    job = FactoryJob.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    
    return jsonify({'message': 'Factory job deleted successfully'})

@factory_bp.route('/project/<project_id>/status', methods=['GET'])
def get_project_factory_status(project_id):
    """Get factory status for specific project"""
    jobs = FactoryJob.query.filter_by(project_id=project_id).order_by(FactoryJob.created_at.desc()).all()
    
    # Get latest job
    latest_job = jobs[0] if jobs else None
    
    # Check if FINAL_SPEC exists
    final_spec_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'workspace', project_id, 'FINAL_SPEC.md')
    has_final_spec = os.path.exists(final_spec_path)
    
    return jsonify({
        'jobs': [j.to_dict() for j in jobs],
        'latest_job': latest_job.to_dict() if latest_job else None,
        'has_final_spec': has_final_spec,
        'ready_for_layer3': has_final_spec and (latest_job and latest_job.status == 'completed' and latest_job.stage == 'freeze')
    })
