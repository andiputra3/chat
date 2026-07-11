from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class Project(db.Model):
    """Model untuk menyimpan informasi proyek"""
    __tablename__ = 'projects'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    version = db.Column(db.String(50), default='1.0.0')
    status = db.Column(db.String(50), default='active')  # active, archived, deleted
    
    # Layer status
    layer1_ready = db.Column(db.Boolean, default=True)
    layer2_status = db.Column(db.String(50), default='not_started')  # not_started, in_progress, ready_for_review, approved, frozen
    layer3_status = db.Column(db.String(50), default='not_started')  # not_started, planning, building, testing, completed
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    chats = db.relationship('Chat', backref='project', lazy=True, cascade='all, delete-orphan')
    factory_jobs = db.relationship('FactoryJob', backref='project', lazy=True, cascade='all, delete-orphan')
    builds = db.relationship('Build', backref='project', lazy=True, cascade='all, delete-orphan')
    timelines = db.relationship('Timeline', backref='project', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'status': self.status,
            'layer2_status': self.layer2_status,
            'layer3_status': self.layer3_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Chat(db.Model):
    """Model untuk menyimpan chat sessions"""
    __tablename__ = 'chats'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey('projects.id'), nullable=False)
    title = db.Column(db.String(200), default='New Chat')
    session_id = db.Column(db.String(100))
    is_pinned = db.Column(db.Boolean, default=False)
    is_archived = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    messages = db.relationship('Message', backref='chat', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'title': self.title,
            'session_id': self.session_id,
            'is_pinned': self.is_pinned,
            'is_archived': self.is_archived,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Message(db.Model):
    """Model untuk menyimpan pesan chat"""
    __tablename__ = 'messages'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    chat_id = db.Column(db.String(36), db.ForeignKey('chats.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # user, assistant, system
    content = db.Column(db.Text, nullable=False)
    thinking = db.Column(db.Text)  # Thinking block dari AI
    attachments = db.Column(db.Text)  # JSON array of file paths
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'chat_id': self.chat_id,
            'role': self.role,
            'content': self.content,
            'thinking': self.thinking,
            'attachments': self.attachments,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class WorkspaceMemory(db.Model):
    """Model untuk AI Workspace Memory"""
    __tablename__ = 'workspace_memory'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey('projects.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # decisions, architecture, requirements, constraints, references, notes, todo
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    tags = db.Column(db.Text)  # JSON array of tags
    is_snapshot = db.Column(db.Boolean, default=False)
    version = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'category': self.category,
            'title': self.title,
            'content': self.content,
            'tags': self.tags,
            'is_snapshot': self.is_snapshot,
            'version': self.version,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class FactoryJob(db.Model):
    """Model untuk Factory Queue (Layer 2)"""
    __tablename__ = 'factory_jobs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    queue_id = db.Column(db.String(20), unique=True, nullable=False)
    project_id = db.Column(db.String(36), db.ForeignKey('projects.id'), nullable=False)
    stage = db.Column(db.String(50), default='input')  # input, analysis, first_spec, documents, validation, compilation, freeze
    status = db.Column(db.String(50), default='waiting')  # waiting, running, ready_for_review, approved, rejected, completed, failed
    progress = db.Column(db.Integer, default=0)  # 0-100
    
    # Timestamps WIB
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Results
    error_message = db.Column(db.Text)
    output_path = db.Column(db.String(500))
    
    def to_dict(self):
        return {
            'id': self.id,
            'queue_id': self.queue_id,
            'project_id': self.project_id,
            'stage': self.stage,
            'status': self.status,
            'progress': self.progress,
            'created_at': self.created_at.strftime('%d %b %Y %H:%M:%S WIB') if self.created_at else None,
            'started_at': self.started_at.strftime('%d %b %Y %H:%M:%S WIB') if self.started_at else None,
            'updated_at': self.updated_at.strftime('%d %b %Y %H:%M:%S WIB') if self.updated_at else None,
            'completed_at': self.completed_at.strftime('%d %b %Y %H:%M:%S WIB') if self.completed_at else None,
            'error_message': self.error_message,
            'output_path': self.output_path
        }


class Build(db.Model):
    """Model untuk Build History (Layer 3)"""
    __tablename__ = 'builds'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey('projects.id'), nullable=False)
    build_number = db.Column(db.Integer, default=1)
    status = db.Column(db.String(50), default='pending')  # pending, planning, building, testing, completed, failed
    ai_provider = db.Column(db.String(50))
    model = db.Column(db.String(100))
    agent = db.Column(db.String(50), default='build')
    
    # Stats
    files_generated = db.Column(db.Integer, default=0)
    lines_generated = db.Column(db.Integer, default=0)
    duration_seconds = db.Column(db.Integer, default=0)
    
    # Timestamps
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Output
    report_path = db.Column(db.String(500))
    source_path = db.Column(db.String(500))
    error_message = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'build_number': self.build_number,
            'status': self.status,
            'ai_provider': self.ai_provider,
            'model': self.model,
            'agent': self.agent,
            'files_generated': self.files_generated,
            'lines_generated': self.lines_generated,
            'duration_seconds': self.duration_seconds,
            'started_at': self.started_at.strftime('%d %b %Y %H:%M:%S WIB') if self.started_at else None,
            'completed_at': self.completed_at.strftime('%d %b %Y %H:%M:%S WIB') if self.completed_at else None,
            'created_at': self.created_at.strftime('%d %b %Y %H:%M:%S WIB') if self.created_at else None,
            'report_path': self.report_path,
            'source_path': self.source_path,
            'error_message': self.error_message
        }


class Timeline(db.Model):
    """Model untuk Timeline events"""
    __tablename__ = 'timelines'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey('projects.id'), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)  # chat, decision, requirement, benchmark, factory, build, git, release
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    event_metadata = db.Column(db.Text)  # JSON - renamed from metadata to avoid conflict
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'event_type': self.event_type,
            'title': self.title,
            'description': self.description,
            'metadata': self.event_metadata,
            'created_at': self.created_at.strftime('%d %b %Y %H:%M:%S WIB') if self.created_at else None
        }


class Notification(db.Model):
    """Model untuk notifications"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    type = db.Column(db.String(50), nullable=False)  # ai_task, factory_job, build_complete, review_required, git_event, benchmark_complete, system_alert
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    project_id = db.Column(db.String(36), db.ForeignKey('projects.id'))
    telegram_sent = db.Column(db.Boolean, default=False)
    telegram_message_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'is_read': self.is_read,
            'project_id': self.project_id,
            'telegram_sent': self.telegram_sent,
            'telegram_message_id': self.telegram_message_id,
            'created_at': self.created_at.strftime('%d %b %Y %H:%M:%S WIB') if self.created_at else None
        }
