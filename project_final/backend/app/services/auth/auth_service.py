"""
Authentication Service
Handles JWT token generation, validation, and user authentication
"""
import jwt
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from functools import wraps
from flask import request, jsonify, g
import os


class AuthService:
    """JWT-based Authentication Service"""
    
    def __init__(self):
        self.secret_key = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
        self.algorithm = 'HS256'
        self.token_expiry_hours = int(os.environ.get('JWT_EXPIRY_HOURS', '24'))
        
        # Default users (in production, these should be in database)
        self.users = {
            'admin': {
                'id': '1',
                'username': 'admin',
                'password_hash': self._hash_password('admin123'),
                'role': 'admin',
                'permissions': ['read', 'write', 'delete', 'admin']
            },
            'developer': {
                'id': '2',
                'username': 'developer',
                'password_hash': self._hash_password('dev123'),
                'role': 'developer',
                'permissions': ['read', 'write']
            },
            'viewer': {
                'id': '3',
                'username': 'viewer',
                'password_hash': self._hash_password('viewer123'),
                'role': 'viewer',
                'permissions': ['read']
            }
        }
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user and return user info if valid"""
        user = self.users.get(username)
        if not user:
            return None
        
        password_hash = self._hash_password(password)
        if user['password_hash'] != password_hash:
            return None
        
        return {
            'id': user['id'],
            'username': user['username'],
            'role': user['role'],
            'permissions': user['permissions']
        }
    
    def generate_token(self, user: Dict[str, Any]) -> str:
        """Generate JWT token for authenticated user"""
        payload = {
            'user_id': user['id'],
            'username': user['username'],
            'role': user['role'],
            'permissions': user['permissions'],
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=self.token_expiry_hours)
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token and return payload if valid"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def has_permission(self, user: Dict[str, Any], permission: str) -> bool:
        """Check if user has specific permission"""
        return permission in user.get('permissions', [])
    
    def require_auth(self, f):
        """Decorator to require authentication for route"""
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            
            # Get token from header
            if 'Authorization' in request.headers:
                auth_header = request.headers['Authorization']
                if auth_header.startswith('Bearer '):
                    token = auth_header.split(' ')[1]
            
            if not token:
                return jsonify({'error': 'Authentication required'}), 401
            
            payload = self.validate_token(token)
            if not payload:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            g.current_user = payload
            return f(*args, **kwargs)
        
        return decorated
    
    def require_role(self, *roles):
        """Decorator to require specific role(s) for route"""
        def decorator(f):
            @wraps(f)
            @self.require_auth
            def decorated(*args, **kwargs):
                if g.current_user['role'] not in roles:
                    return jsonify({'error': 'Insufficient permissions'}), 403
                return f(*args, **kwargs)
            return decorated
        return decorator
    
    def require_permission(self, *permissions):
        """Decorator to require specific permission(s) for route"""
        def decorator(f):
            @wraps(f)
            @self.require_auth
            def decorated(*args, **kwargs):
                user_permissions = g.current_user.get('permissions', [])
                if not any(perm in user_permissions for perm in permissions):
                    return jsonify({'error': 'Insufficient permissions'}), 403
                return f(*args, **kwargs)
            return decorated
        return decorator


# Global instance
auth_service = AuthService()
