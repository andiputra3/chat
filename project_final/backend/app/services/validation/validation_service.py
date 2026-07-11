"""
Validation Service
Cross-artifact validation, consistency checking, and conflict detection
"""
import os
import re
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime


class ValidationService:
    """Service for validating specifications and detecting conflicts"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
    
    def validate_all(self, docs_path: str) -> Dict[str, Any]:
        """Run all validations on specification documents"""
        self.errors = []
        self.warnings = []
        self.info = []
        
        if not os.path.exists(docs_path):
            return {
                'valid': False,
                'errors': ['Documents path does not exist'],
                'warnings': [],
                'info': []
            }
        
        # Get all specification files
        spec_files = self._get_spec_files(docs_path)
        
        # Run validations
        self._validate_file_structure(spec_files)
        self._validate_id_consistency(spec_files)
        self._validate_cross_references(spec_files)
        self._validate_dependencies(spec_files)
        self._validate_forbidden_rules(spec_files)
        self._validate_completeness(spec_files)
        
        return {
            'valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'info': self.info,
            'timestamp': datetime.utcnow().isoformat(),
            'files_checked': len(spec_files)
        }
    
    def _get_spec_files(self, docs_path: str) -> List[str]:
        """Get all specification markdown files"""
        files = []
        for file in os.listdir(docs_path):
            if file.endswith('.md') and file != 'README.md':
                files.append(os.path.join(docs_path, file))
        return files
    
    def _validate_file_structure(self, files: List[str]):
        """Validate that all required files exist and have proper structure"""
        required_files = [
            'PROJECT_IDENTITY',
            'CONSTITUTION',
            'REQUIREMENTS',
            'VARIABLES',
            'FUNCTIONS',
            'PIPELINE',
            'DATA_CONTRACTS',
            'STATE_MACHINES',
            'DEPENDENCY_MATRIX',
            'BUSINESS_RULES',
            'TEST_CASES',
            'FORBIDDEN_RULES',
            'ID_TRACKING',
            'OBJECT_DICTIONARY',
            'EVENT_DICTIONARY',
            'STATE_DICTIONARY',
            'PATTERN_DICTIONARY',
            'FEATURE_REGISTRY',
            'INTERACTION_MATRIX',
            'AI_BUILD_GUARD'
        ]
        
        file_names = [os.path.basename(f).upper() for f in files]
        
        for required in required_files:
            found = any(required in fn for fn in file_names)
            if not found:
                self.errors.append(f"Missing required file: {required}")
    
    def _validate_id_consistency(self, files: List[str]):
        """Validate ID patterns are consistent across files"""
        id_patterns = {
            'VAR': r'VAR-\d{3}',
            'FN': r'FN-\d{3}',
            'STAGE': r'STAGE-\d{3}',
            'DC': r'DC-\d{3}',
            'SM': r'SM-\d{3}',
            'DEP': r'DEP-\d{3}',
            'BR': r'BR-\d{3}',
            'TC': r'TC-\d{3}',
            'FR': r'FR-\d{3}',
            'OBJ': r'OBJ-\d{3}',
            'EVT': r'EVT-\d{3}',
            'STATE': r'STATE-\d{3}',
            'PAT': r'PAT-\d{3}',
            'FEAT': r'FEAT-\d{3}',
            'INT': r'INT-\d{3}',
            'GUARD': r'GUARD-\d{3}'
        }
        
        all_ids = {}
        
        for filepath in files:
            with open(filepath, 'r') as f:
                content = f.read()
            
            for pattern_name, pattern in id_patterns.items():
                matches = re.findall(pattern, content)
                if pattern_name not in all_ids:
                    all_ids[pattern_name] = []
                all_ids[pattern_name].extend(matches)
        
        # Check for duplicates within each type
        for id_type, ids in all_ids.items():
            unique_ids = set(ids)
            if len(ids) != len(unique_ids):
                duplicates = [id for id in ids if ids.count(id) > 1]
                self.errors.append(f"Duplicate {id_type} IDs found: {set(duplicates)}")
    
    def _validate_cross_references(self, files: List[str]):
        """Validate that cross-references between documents are valid"""
        # Read all file contents
        contents = {}
        for filepath in files:
            with open(filepath, 'r') as f:
                contents[os.path.basename(filepath)] = f.read()
        
        # Check REQUIREMENTS references TEST_CASES
        if 'REQUIREMENTS' in str(contents.keys()):
            req_content = next((c for k, c in contents.items() if 'REQUIREMENTS' in k), '')
            tc_content = next((c for k, c in contents.items() if 'TEST_CASES' in k), '')
            
            # Extract requirement IDs
            req_ids = re.findall(r'REQ-\d{3}', req_content)
            
            # Check if each requirement has corresponding test case
            for req_id in req_ids:
                if req_id not in tc_content:
                    self.warnings.append(f"Requirement {req_id} may not have corresponding test case")
    
    def _validate_dependencies(self, files: List[str]):
        """Validate dependency matrix consistency"""
        dep_file = next((f for f in files if 'DEPENDENCY_MATRIX' in f), None)
        
        if not dep_file:
            self.warnings.append("No DEPENDENCY_MATRIX file found")
            return
        
        with open(dep_file, 'r') as f:
            dep_content = f.read()
        
        # Check for circular dependencies (basic check)
        # This is a simplified check - real implementation would build a graph
        if 'circular' in dep_content.lower():
            self.errors.append("Circular dependencies detected in DEPENDENCY_MATRIX")
    
    def _validate_forbidden_rules(self, files: List[str]):
        """Validate that no forbidden rules are violated"""
        forbidden_file = next((f for f in files if 'FORBIDDEN_RULES' in f), None)
        
        if not forbidden_file:
            self.info.append("No FORBIDDEN_RULES file found")
            return
        
        with open(forbidden_file, 'r') as f:
            forbidden_content = f.read()
        
        # Extract forbidden patterns
        forbidden_patterns = re.findall(r'FORBIDDEN:\s*(.+)', forbidden_content, re.IGNORECASE)
        
        # Check other files for violations
        for filepath in files:
            if filepath == forbidden_file:
                continue
            
            with open(filepath, 'r') as f:
                content = f.read()
            
            for pattern in forbidden_patterns:
                if pattern.strip().lower() in content.lower():
                    self.errors.append(f"Forbidden rule violation in {os.path.basename(filepath)}: {pattern}")
    
    def _validate_completeness(self, files: List[str]):
        """Validate that all sections are present in each file"""
        required_sections = {
            'CONSTITUTION': ['Purpose', 'Scope', 'Rules'],
            'REQUIREMENTS': ['Functional', 'Non-Functional'],
            'VARIABLES': ['Description', 'Type', 'Default'],
            'FUNCTIONS': ['Signature', 'Description', 'Parameters'],
            'TEST_CASES': ['Scenario', 'Steps', 'Expected']
        }
        
        for filepath in files:
            filename = os.path.basename(filepath).upper()
            
            with open(filepath, 'r') as f:
                content = f.read()
            
            for file_key, sections in required_sections.items():
                if file_key in filename:
                    for section in sections:
                        if section.lower() not in content.lower():
                            self.warnings.append(
                                f"{filename} may be missing '{section}' section"
                            )
    
    def validate_build_readiness(self, docs_path: str) -> Dict[str, Any]:
        """Calculate build readiness score"""
        validation_result = self.validate_all(docs_path)
        
        if not validation_result['valid']:
            return {
                'ready': False,
                'score': 0,
                'errors': validation_result['errors'],
                'message': 'Specification validation failed'
            }
        
        # Calculate score based on completeness
        score = 100
        
        # Deduct for warnings
        score -= len(validation_result['warnings']) * 2
        
        # Ensure score is between 0 and 100
        score = max(0, min(100, score))
        
        ready = score >= 70  # Minimum 70/100 to be ready
        
        return {
            'ready': ready,
            'score': score,
            'errors': validation_result['errors'],
            'warnings': validation_result['warnings'],
            'message': 'Ready for build' if ready else 'Score below threshold (70)',
            'timestamp': datetime.utcnow().isoformat()
        }


# Global instance
validation_service = ValidationService()
