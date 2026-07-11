"""
AI Gateway Service
Provides unified interface for multiple AI providers (OpenCode, Claude, etc.)
"""
import subprocess
import json
import os
import asyncio
from typing import Optional, Dict, Any, Generator
from datetime import datetime


class AIGateway:
    """Unified AI Provider Gateway"""
    
    def __init__(self):
        self.providers = {
            'opencode': OpenCodeService(),
            'claude': ClaudeService()
        }
        self.default_provider = os.environ.get('DEFAULT_AI_PROVIDER', 'opencode')
    
    def get_provider(self, provider_name: str = None):
        """Get AI provider service"""
        name = provider_name or self.default_provider
        if name not in self.providers:
            raise ValueError(f"Unknown provider: {name}")
        return self.providers[name]
    
    async def chat(self, 
                   messages: list, 
                   provider: str = None,
                   model: str = None,
                   mode: str = 'build',
                   project_id: str = None,
                   session_id: str = None,
                   stream: bool = False) -> Dict[str, Any]:
        """Send chat request to AI provider"""
        service = self.get_provider(provider)
        return await service.chat(
            messages=messages,
            model=model,
            mode=mode,
            project_id=project_id,
            session_id=session_id,
            stream=stream
        )
    
    async def execute_build(self,
                           spec_path: str,
                           workspace_path: str,
                           provider: str = None,
                           model: str = None,
                           agent: str = 'build') -> Dict[str, Any]:
        """Execute AI build from specification"""
        service = self.get_provider(provider)
        return await service.execute_build(
            spec_path=spec_path,
            workspace_path=workspace_path,
            model=model,
            agent=agent
        )
    
    def count_tokens(self, text: str) -> int:
        """Estimate token count"""
        # Rough estimation: 1 token ≈ 4 characters for code
        return len(text) // 4
    
    def estimate_cost(self, tokens: int, provider: str = None) -> float:
        """Estimate cost based on token count"""
        service = self.get_provider(provider)
        return service.estimate_cost(tokens)


class OpenCodeService:
    """OpenCode CLI Service"""
    
    def __init__(self):
        self.cli_command = 'opencode'
        self.default_model = os.environ.get('OPENCODE_MODEL', 'deepseek-v4-flash-free')
    
    async def chat(self,
                   messages: list,
                   model: str = None,
                   mode: str = 'build',
                   project_id: str = None,
                   session_id: str = None,
                   stream: bool = False) -> Dict[str, Any]:
        """Send chat to OpenCode"""
        model = model or self.default_model
        
        # Build command
        cmd = [self.cli_command]
        
        if mode == 'plan':
            cmd.extend(['--mode', 'plan'])
        
        if model:
            cmd.extend(['--model', model])
        
        # Add conversation history
        for msg in messages:
            if msg['role'] == 'user':
                cmd.extend(['-u', msg['content']])
            elif msg['role'] == 'assistant':
                cmd.extend(['-a', msg['content']])
        
        try:
            # Execute OpenCode CLI
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=int(os.environ.get('AI_TIMEOUT', '600'))
            )
            
            return {
                'success': result.returncode == 0,
                'response': result.stdout,
                'error': result.stderr if result.returncode != 0 else None,
                'provider': 'opencode',
                'model': model,
                'tokens_used': self._count_tokens(result.stdout),
                'timestamp': datetime.utcnow().isoformat()
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'response': None,
                'error': 'Request timed out',
                'provider': 'opencode',
                'model': model,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'response': None,
                'error': str(e),
                'provider': 'opencode',
                'model': model,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def execute_build(self,
                           spec_path: str,
                           workspace_path: str,
                           model: str = None,
                           agent: str = 'build') -> Dict[str, Any]:
        """Execute build with OpenCode"""
        model = model or self.default_model
        
        # Read specification
        with open(spec_path, 'r') as f:
            spec_content = f.read()
        
        # Build prompt
        prompt = f"""You are an expert software builder. 
Your task is to generate complete source code based on the following specification.

SPECIFICATION:
{spec_content}

INSTRUCTIONS:
1. Read and understand the entire specification
2. Generate all required files according to the folder structure
3. Follow all coding conventions and patterns specified
4. Do NOT modify any .md files in /docs/ folder
5. Output all source code directly to the workspace folder
6. Ensure all tests pass before completing

Begin building now."""
        
        cmd = [self.cli_command, '--model', model]
        
        if agent == 'plan':
            cmd.extend(['--mode', 'plan'])
        
        cmd.extend(['-u', prompt])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=workspace_path,
                timeout=int(os.environ.get('BUILD_TIMEOUT', '1800'))
            )
            
            # Count generated files
            files_generated = self._count_files(workspace_path)
            lines_generated = self._count_lines(workspace_path)
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr if result.returncode != 0 else None,
                'files_generated': files_generated,
                'lines_generated': lines_generated,
                'provider': 'opencode',
                'model': model,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'output': None,
                'error': str(e),
                'files_generated': 0,
                'lines_generated': 0,
                'provider': 'opencode',
                'model': model,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _count_files(self, path: str) -> int:
        """Count files in directory"""
        count = 0
        for root, dirs, files in os.walk(path):
            # Skip docs folder
            if 'docs' in root:
                continue
            count += len(files)
        return count
    
    def _count_lines(self, path: str) -> int:
        """Count lines of code in directory"""
        total = 0
        for root, dirs, files in os.walk(path):
            if 'docs' in root:
                continue
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.tsx', '.html', '.css')):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r') as f:
                            total += sum(1 for _ in f)
                    except:
                        pass
        return total
    
    def _count_tokens(self, text: str) -> int:
        """Estimate token count"""
        return len(text) // 4
    
    def estimate_cost(self, tokens: int) -> float:
        """Estimate cost (OpenCode may be free depending on model)"""
        # Placeholder - adjust based on actual pricing
        return 0.0


class ClaudeService:
    """Claude Code CLI Service"""
    
    def __init__(self):
        self.cli_command = 'claude'
        self.default_model = os.environ.get('CLAUDE_MODEL', 'claude-sonnet-4-20250514')
    
    async def chat(self,
                   messages: list,
                   model: str = None,
                   mode: str = 'build',
                   project_id: str = None,
                   session_id: str = None,
                   stream: bool = False) -> Dict[str, Any]:
        """Send chat to Claude Code"""
        model = model or self.default_model
        
        cmd = [self.cli_command]
        
        if mode == 'plan':
            cmd.extend(['--mode', 'plan'])
        
        if model:
            cmd.extend(['--model', model])
        
        # Add conversation
        for msg in messages:
            if msg['role'] == 'user':
                cmd.extend(['-u', msg['content']])
            elif msg['role'] == 'assistant':
                cmd.extend(['-a', msg['content']])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=int(os.environ.get('AI_TIMEOUT', '600'))
            )
            
            return {
                'success': result.returncode == 0,
                'response': result.stdout,
                'error': result.stderr if result.returncode != 0 else None,
                'provider': 'claude',
                'model': model,
                'tokens_used': self._count_tokens(result.stdout),
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'response': None,
                'error': str(e),
                'provider': 'claude',
                'model': model,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def execute_build(self,
                           spec_path: str,
                           workspace_path: str,
                           model: str = None,
                           agent: str = 'build') -> Dict[str, Any]:
        """Execute build with Claude Code"""
        model = model or self.default_model
        
        with open(spec_path, 'r') as f:
            spec_content = f.read()
        
        prompt = f"""You are an expert software builder.
Generate complete source code based on this specification:

{spec_content}

Follow all specifications exactly. Output code to workspace folder."""
        
        cmd = [self.cli_command, '--model', model, '-u', prompt]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=workspace_path,
                timeout=int(os.environ.get('BUILD_TIMEOUT', '1800'))
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr if result.returncode != 0 else None,
                'provider': 'claude',
                'model': model,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'output': None,
                'error': str(e),
                'provider': 'claude',
                'model': model,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _count_tokens(self, text: str) -> int:
        return len(text) // 4
    
    def estimate_cost(self, tokens: int) -> float:
        # Placeholder - Claude pricing varies
        return tokens * 0.00001  # Example rate
