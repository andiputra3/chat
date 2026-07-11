"""
Knowledge Library Service
Manages project constitution, SOPs, rules, and institutional memory
"""
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class KnowledgeLibrary:
    """Central repository for project knowledge and rules"""
    
    def __init__(self, base_path: str = None):
        self.base_path = base_path or os.path.join(os.path.dirname(__file__), '..', '..', '..', 'knowledge')
        self.ensure_structure()
    
    def ensure_structure(self):
        """Create knowledge library folder structure"""
        folders = [
            'constitutions',
            'sops',
            'rules',
            'patterns',
            'templates',
            'guides',
            'decisions'
        ]
        
        for folder in folders:
            path = os.path.join(self.base_path, folder)
            os.makedirs(path, exist_ok=True)
    
    def save_constitution(self, project_id: str, content: str) -> str:
        """Save project constitution"""
        filename = f"CONSTITUTION_{project_id}.md"
        filepath = os.path.join(self.base_path, 'constitutions', filename)
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        return filepath
    
    def get_constitution(self, project_id: str) -> Optional[str]:
        """Get project constitution"""
        filename = f"CONSTITUTION_{project_id}.md"
        filepath = os.path.join(self.base_path, 'constitutions', filename)
        
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'r') as f:
            return f.read()
    
    def save_sop(self, name: str, content: str, category: str = 'general') -> str:
        """Save Standard Operating Procedure"""
        filename = f"SOP_{name.replace(' ', '_').upper()}.md"
        filepath = os.path.join(self.base_path, 'sops', category, filename)
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        return filepath
    
    def get_sop(self, name: str, category: str = 'general') -> Optional[str]:
        """Get SOP by name"""
        filename = f"SOP_{name.replace(' ', '_').upper()}.md"
        filepath = os.path.join(self.base_path, 'sops', category, filename)
        
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'r') as f:
            return f.read()
    
    def list_sops(self, category: str = None) -> List[Dict[str, Any]]:
        """List all SOPs"""
        sops = []
        sop_path = os.path.join(self.base_path, 'sops')
        
        for root, dirs, files in os.walk(sop_path):
            for file in files:
                if file.endswith('.md'):
                    rel_path = os.path.relpath(root, sop_path)
                    sops.append({
                        'name': file.replace('SOP_', '').replace('.md', '').replace('_', ' '),
                        'category': rel_path if rel_path != '.' else 'general',
                        'path': os.path.join(root, file)
                    })
        
        if category:
            sops = [sop for sop in sops if sop['category'] == category]
        
        return sops
    
    def save_rule(self, rule_type: str, rule_id: str, content: str) -> str:
        """Save business rule or forbidden rule"""
        filename = f"{rule_type.upper()}_{rule_id}.md"
        filepath = os.path.join(self.base_path, 'rules', filename)
        
        with open(filepath, 'w') as f:
            f.write(f"# {rule_type.upper()} {rule_id}\n\n{content}")
        
        return filepath
    
    def get_rules(self, rule_type: str = None) -> List[Dict[str, Any]]:
        """Get all rules or filter by type"""
        rules = []
        rules_path = os.path.join(self.base_path, 'rules')
        
        if not os.path.exists(rules_path):
            return rules
        
        for file in os.listdir(rules_path):
            if file.endswith('.md'):
                filepath = os.path.join(rules_path, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                
                # Parse rule type and ID from filename
                parts = file.replace('.md', '').split('_')
                if len(parts) >= 2:
                    r_type = parts[0]
                    r_id = parts[1]
                    
                    if rule_type is None or r_type.upper() == rule_type.upper():
                        rules.append({
                            'type': r_type,
                            'id': r_id,
                            'content': content,
                            'path': filepath
                        })
        
        return rules
    
    def save_pattern(self, pattern_name: str, pattern_content: str) -> str:
        """Save design pattern"""
        filename = f"PATTERN_{pattern_name.replace(' ', '_').upper()}.md"
        filepath = os.path.join(self.base_path, 'patterns', filename)
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        return filepath
    
    def get_patterns(self) -> List[Dict[str, Any]]:
        """Get all design patterns"""
        patterns = []
        patterns_path = os.path.join(self.base_path, 'patterns')
        
        if not os.path.exists(patterns_path):
            return patterns
        
        for file in os.listdir(patterns_path):
            if file.endswith('.md'):
                filepath = os.path.join(patterns_path, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                
                patterns.append({
                    'name': file.replace('PATTERN_', '').replace('.md', '').replace('_', ' '),
                    'content': content,
                    'path': filepath
                })
        
        return patterns
    
    def save_decision(self, decision_id: str, title: str, description: str, 
                     alternatives: List[str], rationale: str, status: str = 'approved') -> str:
        """Save architecture or business decision"""
        filename = f"DECISION_{decision_id}.md"
        filepath = os.path.join(self.base_path, 'decisions', filename)
        
        content = f"""# Decision {decision_id}: {title}

## Status
{status}

## Description
{description}

## Alternatives Considered
"""
        for alt in alternatives:
            content += f"- {alt}\n"
        
        content += f"\n## Rationale\n{rationale}\n"
        content += f"\n## Date\n{datetime.utcnow().isoformat()}\n"
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        return filepath
    
    def get_decisions(self) -> List[Dict[str, Any]]:
        """Get all decisions"""
        decisions = []
        decisions_path = os.path.join(self.base_path, 'decisions')
        
        if not os.path.exists(decisions_path):
            return decisions
        
        for file in os.listdir(decisions_path):
            if file.endswith('.md'):
                filepath = os.path.join(decisions_path, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                
                decisions.append({
                    'id': file.replace('DECISION_', '').replace('.md', ''),
                    'content': content,
                    'path': filepath
                })
        
        return decisions
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search knowledge library"""
        results = []
        query_lower = query.lower()
        
        for root, dirs, files in os.walk(self.base_path):
            for file in files:
                if file.endswith('.md'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r') as f:
                            content = f.read()
                        
                        if query_lower in content.lower():
                            results.append({
                                'file': file,
                                'path': filepath,
                                'snippet': self._extract_snippet(content, query_lower)
                            })
                    except:
                        pass
        
        return results
    
    def _extract_snippet(self, content: str, query: str, context_size: int = 100) -> str:
        """Extract snippet around query match"""
        idx = content.lower().find(query)
        if idx == -1:
            return content[:200]
        
        start = max(0, idx - context_size)
        end = min(len(content), idx + len(query) + context_size)
        
        return "..." + content[start:end] + "..."


# Global instance
knowledge_library = KnowledgeLibrary()
