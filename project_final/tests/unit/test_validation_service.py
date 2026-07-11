"""
Unit Tests for Validation Service
"""
import pytest
import sys
import os
import tempfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from app.services.validation.validation_service import ValidationService, validation_service


class TestValidationService:
    """Test cases for ValidationService class"""
    
    def test_init(self):
        """Test ValidationService initialization"""
        service = ValidationService()
        assert service.errors == []
        assert service.warnings == []
        assert service.info == []
    
    def test_validate_all_nonexistent_path(self):
        """Test validation with nonexistent path"""
        service = ValidationService()
        result = service.validate_all('/nonexistent/path')
        
        assert result['valid'] is False
        assert len(result['errors']) > 0
    
    def test_validate_all_empty_directory(self, tmp_path):
        """Test validation with empty directory"""
        service = ValidationService()
        result = service.validate_all(str(tmp_path))
        
        assert result['valid'] is False
        assert 'Missing required file' in str(result['errors'])
    
    def test_build_readiness_below_threshold(self, tmp_path):
        """Test build readiness score below threshold"""
        service = ValidationService()
        
        # Create minimal docs structure
        (tmp_path / 'PROJECT_IDENTITY_TEST.md').write_text('# Test')
        
        result = service.validate_build_readiness(str(tmp_path))
        
        assert result['ready'] is False
        assert result['score'] < 70
    
    def test_get_spec_files(self, tmp_path):
        """Test getting specification files"""
        service = ValidationService()
        
        # Create test files
        (tmp_path / 'TEST1.md').write_text('content1')
        (tmp_path / 'TEST2.md').write_text('content2')
        (tmp_path / 'README.md').write_text('readme')
        (tmp_path / 'test.txt').write_text('not markdown')
        
        files = service._get_spec_files(str(tmp_path))
        
        # Should include .md files except README.md
        assert len(files) == 2
        assert all(f.endswith('.md') for f in files)
        assert not any('README' in f for f in files)


class TestValidationServiceWithSpecs:
    """Integration tests with actual specification files"""
    
    @pytest.fixture
    def spec_dir(self, tmp_path):
        """Create temporary directory with spec files"""
        # Create minimal required files
        files = [
            '00_PROJECT_IDENTITY_TEST.md',
            '01_CONSTITUTION_TEST.md',
            '02_REQUIREMENTS_TEST.md',
        ]
        
        for filename in files:
            (tmp_path / filename).write_text(f'# {filename}\n\nContent here')
        
        return tmp_path
    
    def test_validate_file_structure(self, spec_dir):
        """Test file structure validation"""
        service = ValidationService()
        result = service.validate_all(str(spec_dir))
        
        # Should have errors for missing files
        assert len(result['errors']) > 0
        assert 'Missing required file' in str(result['errors'])


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
