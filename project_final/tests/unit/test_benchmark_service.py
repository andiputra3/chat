"""
Unit tests for Benchmark Service
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
sys.path.insert(0, '/workspace/project_final/backend')

from app.services.benchmark.benchmark_service import BenchmarkService


class TestBenchmarkService:
    """Test cases for BenchmarkService."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.service = BenchmarkService()
    
    def test_measure_api_response_time_success(self):
        """Test measuring successful API response time."""
        def mock_func():
            return {"data": "test"}
        
        result = self.service.measure_api_response_time("test_endpoint", mock_func)
        
        assert result["success"] is True
        assert result["endpoint"] == "test_endpoint"
        assert "response_time_ms" in result
        assert "memory_used_mb" in result
        assert result["error"] is None
    
    def test_measure_api_response_time_failure(self):
        """Test measuring failed API response time."""
        def mock_func():
            raise Exception("Test error")
        
        result = self.service.measure_api_response_time("test_endpoint", mock_func)
        
        assert result["success"] is False
        assert result["error"] == "Test error"
        assert result["endpoint"] == "test_endpoint"
    
    def test_get_system_metrics(self):
        """Test getting system metrics."""
        metrics = self.service.get_system_metrics()
        
        assert "timestamp" in metrics
        assert "cpu_percent" in metrics
        assert "memory_percent" in metrics
        assert "disk_percent" in metrics
        assert 0 <= metrics["cpu_percent"] <= 100
        assert 0 <= metrics["memory_percent"] <= 100
    
    def test_run_load_test(self):
        """Test running load test."""
        def mock_func():
            return {"data": "test"}
        
        result = self.service.run_load_test(mock_func, iterations=5)
        
        assert result["total_iterations"] == 5
        assert result["successful_runs"] == 5
        assert result["failed_runs"] == 0
        assert result["success_rate_percent"] == 100.0
        assert "avg_response_time_ms" in result
    
    def test_get_benchmark_history(self):
        """Test getting benchmark history."""
        # Clear existing history
        self.service.clear_benchmark_history()
        
        # Add some benchmarks
        def mock_func():
            return {"data": "test"}
        
        self.service.measure_api_response_time("endpoint1", mock_func)
        self.service.measure_api_response_time("endpoint2", mock_func)
        
        history = self.service.get_benchmark_history(limit=10)
        
        assert len(history) == 2
        assert history[0]["endpoint"] == "endpoint1"
        assert history[1]["endpoint"] == "endpoint2"
    
    def test_clear_benchmark_history(self):
        """Test clearing benchmark history."""
        # Add some benchmarks
        def mock_func():
            return {"data": "test"}
        
        self.service.measure_api_response_time("endpoint1", mock_func)
        self.service.clear_benchmark_history()
        
        history = self.service.get_benchmark_history()
        assert len(history) == 0
    
    def test_generate_benchmark_report_no_data(self):
        """Test generating report with no data."""
        self.service.clear_benchmark_history()
        report = self.service.generate_benchmark_report()
        
        assert report["status"] == "no_data"
    
    def test_generate_benchmark_report_with_data(self):
        """Test generating report with data."""
        self.service.clear_benchmark_history()
        
        def mock_func():
            return {"data": "test"}
        
        self.service.measure_api_response_time("endpoint1", mock_func)
        self.service.measure_api_response_time("endpoint2", mock_func)
        
        report = self.service.generate_benchmark_report()
        
        assert report["total_benchmarks"] == 2
        assert report["successful_benchmarks"] == 2
        assert "overall_success_rate" in report
        assert "average_response_time_ms" in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
