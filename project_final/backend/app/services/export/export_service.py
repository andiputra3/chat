"""
Export Service for AI Project Manager OS
Handles exporting reports, specifications, and data to various formats (PDF, Excel, CSV).
"""

import json
import csv
import io
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path


class ExportService:
    """Service for exporting data to various formats."""
    
    def __init__(self, export_dir: str = "exports"):
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    def export_to_json(self, data: Any, filename: str) -> Dict[str, Any]:
        """Export data to JSON format."""
        filepath = self.export_dir / f"{filename}.json"
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return {
                "success": True,
                "filepath": str(filepath),
                "format": "json",
                "size_bytes": filepath.stat().st_size,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "format": "json"
            }
    
    def export_to_csv(self, data: List[Dict[str, Any]], filename: str) -> Dict[str, Any]:
        """Export list of dictionaries to CSV format."""
        if not data:
            return {
                "success": False,
                "error": "No data to export",
                "format": "csv"
            }
        
        filepath = self.export_dir / f"{filename}.csv"
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            
            return {
                "success": True,
                "filepath": str(filepath),
                "format": "csv",
                "size_bytes": filepath.stat().st_size,
                "rows_exported": len(data),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "format": "csv"
            }
    
    def export_to_txt(self, content: str, filename: str) -> Dict[str, Any]:
        """Export text content to TXT format."""
        filepath = self.export_dir / f"{filename}.txt"
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "filepath": str(filepath),
                "format": "txt",
                "size_bytes": filepath.stat().st_size,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "format": "txt"
            }
    
    def export_report(self, report_data: Dict[str, Any], report_type: str = "comprehensive") -> Dict[str, Any]:
        """Export comprehensive report in multiple formats."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{report_type}_report_{timestamp}"
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "report_type": report_type,
            "exports": {}
        }
        
        # Export to JSON
        json_result = self.export_to_json(report_data, f"{base_filename}")
        results["exports"]["json"] = json_result
        
        # Export summary to CSV if applicable
        if "summary" in report_data and isinstance(report_data["summary"], list):
            csv_result = self.export_to_csv(report_data["summary"], f"{base_filename}_summary")
            results["exports"]["csv"] = csv_result
        
        # Export text version
        txt_content = self._generate_text_report(report_data)
        txt_result = self.export_to_txt(txt_content, f"{base_filename}")
        results["exports"]["txt"] = txt_result
        
        return results
    
    def _generate_text_report(self, data: Dict[str, Any], indent: int = 0) -> str:
        """Generate human-readable text report from dictionary."""
        lines = []
        prefix = "  " * indent
        
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{prefix}{key}:")
                lines.append(self._generate_text_report(value, indent + 1))
            elif isinstance(value, list):
                lines.append(f"{prefix}{key}:")
                for item in value:
                    if isinstance(item, dict):
                        lines.append(self._generate_text_report(item, indent + 1))
                    else:
                        lines.append(f"{prefix}  - {item}")
            else:
                lines.append(f"{prefix}{key}: {value}")
        
        return "\n".join(lines)
    
    def get_export_history(self) -> List[Dict[str, Any]]:
        """Get list of all exported files."""
        exports = []
        
        for filepath in self.export_dir.glob("*"):
            if filepath.is_file():
                exports.append({
                    "filename": filepath.name,
                    "filepath": str(filepath),
                    "size_bytes": filepath.stat().st_size,
                    "created_at": datetime.fromtimestamp(filepath.stat().st_ctime).isoformat(),
                    "modified_at": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
                })
        
        return sorted(exports, key=lambda x: x["modified_at"], reverse=True)
    
    def cleanup_old_exports(self, days: int = 7) -> Dict[str, Any]:
        """Clean up export files older than specified days."""
        from datetime import timedelta
        
        cutoff_time = datetime.now() - timedelta(days=days)
        deleted_files = []
        
        for filepath in self.export_dir.glob("*"):
            if filepath.is_file():
                file_time = datetime.fromtimestamp(filepath.stat().st_mtime)
                if file_time < cutoff_time:
                    try:
                        filepath.unlink()
                        deleted_files.append(filepath.name)
                    except Exception as e:
                        pass  # Log error but continue
        
        return {
            "success": True,
            "deleted_count": len(deleted_files),
            "deleted_files": deleted_files,
            "cutoff_days": days,
            "timestamp": datetime.now().isoformat()
        }


# Singleton instance
export_service = ExportService()
