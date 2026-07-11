"""
Git Service - Git operations via API (no terminal)
Uses GitPython library for all Git operations
"""
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    import git
    from git import Repo, GitCommandError
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False


class GitService:
    """Git operations service"""
    
    def __init__(self):
        if not GIT_AVAILABLE:
            raise ImportError("GitPython not installed. Run: pip install GitPython")
    
    def init_repository(self, path: str) -> Dict[str, Any]:
        """Initialize a new Git repository"""
        try:
            repo = Repo.init(path)
            return {
                'success': True,
                'path': path,
                'message': 'Repository initialized',
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def commit(self, path: str, message: str, files: List[str] = None) -> Dict[str, Any]:
        """Commit changes to repository"""
        try:
            repo = Repo(path)
            
            # Add specified files or all changes
            if files:
                for file in files:
                    repo.index.add([file])
            else:
                repo.index.add(['*'])
            
            # Commit
            commit = repo.index.commit(message)
            
            return {
                'success': True,
                'commit_hash': commit.hexsha,
                'message': message,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def create_branch(self, path: str, branch_name: str, base: str = 'main') -> Dict[str, Any]:
        """Create a new branch"""
        try:
            repo = Repo(path)
            
            # Create branch
            repo.git.checkout('-b', branch_name, base)
            
            return {
                'success': True,
                'branch': branch_name,
                'base': base,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def push(self, path: str, remote: str = 'origin', branch: str = None) -> Dict[str, Any]:
        """Push changes to remote repository"""
        try:
            repo = Repo(path)
            
            if branch is None:
                branch = repo.active_branch.name
            
            result = repo.remote(name=remote).push(branch)
            
            return {
                'success': True,
                'remote': remote,
                'branch': branch,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def pull(self, path: str, remote: str = 'origin', branch: str = None) -> Dict[str, Any]:
        """Pull changes from remote repository"""
        try:
            repo = Repo(path)
            
            if branch is None:
                branch = repo.active_branch.name
            
            repo.remote(name=remote).pull(branch)
            
            return {
                'success': True,
                'remote': remote,
                'branch': branch,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def get_status(self, path: str) -> Dict[str, Any]:
        """Get repository status"""
        try:
            repo = Repo(path)
            
            return {
                'success': True,
                'branch': repo.active_branch.name if hasattr(repo, 'active_branch') else 'unknown',
                'is_dirty': repo.is_dirty(),
                'untracked_files': repo.untracked_files,
                'changes': [item.a_path for item in repo.index.diff(None)],
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def get_log(self, path: str, max_commits: int = 10) -> Dict[str, Any]:
        """Get commit history"""
        try:
            repo = Repo(path)
            
            commits = []
            for commit in list(repo.iter_commits(max_count=max_commits)):
                commits.append({
                    'hash': commit.hexsha,
                    'message': commit.message.strip(),
                    'author': str(commit.author),
                    'date': datetime.fromtimestamp(commit.committed_date).isoformat()
                })
            
            return {
                'success': True,
                'commits': commits,
                'count': len(commits),
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
