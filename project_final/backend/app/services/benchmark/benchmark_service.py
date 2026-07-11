"""
Benchmark Service for AI Project Manager OS
Measures system performance, API response times, and resource usage.
"""

import time
import psutil
import os
from typing import Dict, Any, List
from datetime import datetime


class BenchmarkService:
    """Service for measuring system and application performance."""
    
    def __init__(self):
        self.benchmark_results = []
    
    def measure_api_response_time(self, endpoint: str, func: callable, *args, **kwargs) -> Dict[str, Any]:
        """Measure API response time for a specific endpoint."""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        
        try:
            result = func(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss
        
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        memory_used = (end_memory - start_memory) / 1024 / 1024  # Convert to MB
        
        benchmark_data = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "response_time_ms": round(response_time, 2),
            "memory_used_mb": round(memory_used, 2),
            "success": success,
            "error": error
        }
        
        self.benchmark_results.append(benchmark_data)
        return benchmark_data
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_mb": round(memory.available / 1024 / 1024, 2),
            "disk_percent": disk.percent,
            "disk_free_gb": round(disk.free / 1024 / 1024 / 1024, 2)
        }
    
    def run_load_test(self, func: callable, iterations: int = 10, *args, **kwargs) -> Dict[str, Any]:
        """Run load test by executing a function multiple times."""
        results = []
        
        for i in range(iterations):
            result = self.measure_api_response_time(f"load_test_iteration_{i}", func, *args, **kwargs)
            results.append(result)
        
        successful_runs = [r for r in results if r["success"]]
        avg_response_time = sum(r["response_time_ms"] for r in successful_runs) / len(successful_runs) if successful_runs else 0
        min_response_time = min(r["response_time_ms"] for r in successful_runs) if successful_runs else 0
        max_response_time = max(r["response_time_ms"] for r in successful_runs) if successful_runs else 0
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_iterations": iterations,
            "successful_runs": len(successful_runs),
            "failed_runs": iterations - len(successful_runs),
            "avg_response_time_ms": round(avg_response_time, 2),
            "min_response_time_ms": round(min_response_time, 2),
            "max_response_time_ms": round(max_response_time, 2),
            "success_rate_percent": round((len(successful_runs) / iterations) * 100, 2)
        }
    
    def get_benchmark_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get benchmark history."""
        return self.benchmark_results[-limit:]
    
    def clear_benchmark_history(self):
        """Clear benchmark history."""
        self.benchmark_results = []
    
    def generate_benchmark_report(self) -> Dict[str, Any]:
        """Generate comprehensive benchmark report."""
        if not self.benchmark_results:
            return {"status": "no_data", "message": "No benchmark data available"}
        
        successful = [r for r in self.benchmark_results if r["success"]]
        
        return {
            "generated_at": datetime.now().isoformat(),
            "total_benchmarks": len(self.benchmark_results),
            "successful_benchmarks": len(successful),
            "failed_benchmarks": len(self.benchmark_results) - len(successful),
            "overall_success_rate": round((len(successful) / len(self.benchmark_results)) * 100, 2) if self.benchmark_results else 0,
            "average_response_time_ms": round(sum(r["response_time_ms"] for r in successful) / len(successful), 2) if successful else 0,
            "endpoints_tested": list(set(r["endpoint"] for r in self.benchmark_results)),
            "system_metrics": self.get_system_metrics()
        }


# Singleton instance
benchmark_service = BenchmarkService()
