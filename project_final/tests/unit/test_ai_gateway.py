"""
Unit Tests for AI Gateway Service
"""
import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from app.services.ai.ai_gateway import AIGateway, OpenCodeService, ClaudeService


class TestAIGateway:
    """Test cases for AIGateway class"""
    
    def test_init(self):
        """Test AIGateway initialization"""
        gateway = AIGateway()
        assert 'opencode' in gateway.providers
        assert 'claude' in gateway.providers
        assert gateway.default_provider in ['opencode', 'claude']
    
    def test_get_provider_valid(self):
        """Test getting valid provider"""
        gateway = AIGateway()
        provider = gateway.get_provider('opencode')
        assert isinstance(provider, OpenCodeService)
    
    def test_get_provider_invalid(self):
        """Test getting invalid provider raises error"""
        gateway = AIGateway()
        with pytest.raises(ValueError):
            gateway.get_provider('invalid_provider')
    
    def test_count_tokens(self):
        """Test token counting"""
        gateway = AIGateway()
        text = "Hello World"
        tokens = gateway.count_tokens(text)
        assert tokens == len(text) // 4
    
    def test_estimate_cost(self):
        """Test cost estimation"""
        gateway = AIGateway()
        cost = gateway.estimate_cost(1000, 'opencode')
        assert isinstance(cost, float)


class TestOpenCodeService:
    """Test cases for OpenCodeService class"""
    
    def test_init(self):
        """Test OpenCodeService initialization"""
        service = OpenCodeService()
        assert service.cli_command == 'opencode'
        assert service.default_model is not None
    
    def test_count_files(self, tmp_path):
        """Test file counting"""
        service = OpenCodeService()
        
        # Create test files
        (tmp_path / 'file1.py').write_text('print("hello")')
        (tmp_path / 'file2.js').write_text('console.log("hello")')
        
        count = service._count_files(str(tmp_path))
        assert count >= 2
    
    def test_count_lines(self, tmp_path):
        """Test line counting"""
        service = OpenCodeService()
        
        # Create test file with 5 lines
        test_file = tmp_path / 'test.py'
        test_file.write_text('line1\nline2\nline3\nline4\nline5\n')
        
        lines = service._count_lines(str(tmp_path))
        assert lines >= 5


class TestClaudeService:
    """Test cases for ClaudeService class"""
    
    def test_init(self):
        """Test ClaudeService initialization"""
        service = ClaudeService()
        assert service.cli_command == 'claude'
        assert service.default_model is not None
    
    def test_count_tokens(self):
        """Test token counting for Claude"""
        service = ClaudeService()
        text = "Test content for tokenization"
        tokens = service._count_tokens(text)
        assert tokens == len(text) // 4


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
