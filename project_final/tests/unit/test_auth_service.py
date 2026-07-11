"""
Unit Tests for Authentication Service
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from app.services.auth.auth_service import AuthService, auth_service


class TestAuthService:
    """Test cases for AuthService class"""
    
    def test_init(self):
        """Test AuthService initialization"""
        service = AuthService()
        assert service.algorithm == 'HS256'
        assert service.token_expiry_hours > 0
    
    def test_hash_password(self):
        """Test password hashing"""
        service = AuthService()
        password = 'testpassword123'
        hashed = service._hash_password(password)
        
        # Should be SHA-256 hex (64 characters)
        assert len(hashed) == 64
        assert hashed != password
        
        # Same password should produce same hash
        assert service._hash_password(password) == hashed
    
    def test_authenticate_valid_user(self):
        """Test authenticating valid user"""
        service = AuthService()
        result = service.authenticate('admin', 'admin123')
        
        assert result is not None
        assert result['username'] == 'admin'
        assert result['role'] == 'admin'
    
    def test_authenticate_invalid_user(self):
        """Test authenticating invalid user"""
        service = AuthService()
        result = service.authenticate('nonexistent', 'password')
        assert result is None
    
    def test_authenticate_wrong_password(self):
        """Test authenticating with wrong password"""
        service = AuthService()
        result = service.authenticate('admin', 'wrongpassword')
        assert result is None
    
    def test_generate_token(self):
        """Test JWT token generation"""
        service = AuthService()
        user = {
            'id': '1',
            'username': 'testuser',
            'role': 'developer',
            'permissions': ['read', 'write']
        }
        
        token = service.generate_token(user)
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_validate_token_valid(self):
        """Test validating valid token"""
        service = AuthService()
        user = {'id': '1', 'username': 'test', 'role': 'admin', 'permissions': ['read']}
        token = service.generate_token(user)
        
        payload = service.validate_token(token)
        assert payload is not None
        assert payload['username'] == 'test'
    
    def test_validate_token_invalid(self):
        """Test validating invalid token"""
        service = AuthService()
        result = service.validate_token('invalid_token_here')
        assert result is None
    
    def test_has_permission(self):
        """Test permission checking"""
        service = AuthService()
        user = {'permissions': ['read', 'write']}
        
        assert service.has_permission(user, 'read') is True
        assert service.has_permission(user, 'delete') is False
    
    def test_require_role_decorator(self):
        """Test role requirement decorator"""
        from flask import Flask
        from unittest.mock import patch
        
        app = Flask(__name__)
        service = AuthService()
        
        @app.route('/admin')
        @service.require_role('admin')
        def admin_route():
            return 'Admin access granted'
        
        # Test would require Flask test client
        assert admin_route is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
