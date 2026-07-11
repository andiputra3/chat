import fastifyPlugin from 'fastify-plugin';
import { execSync } from 'child_process';
import path from 'path';
import fs from 'fs';
import db, { logAudit } from '../db/index.js';

async function gitRoutes(fastify, options) {
  // Auth guard for all routes
  fastify.addHook('preHandler', async (request, reply) => {
    try {
      await request.jwtVerify();
    } catch (err) {
      reply.code(401).send({ error: 'Unauthorized', message: 'Invalid token' });
    }
  });

  // Helper function to execute git commands
  function execGit(workspacePath, command) {
    try {
      const result = execSync(command, {
        cwd: workspacePath,
        encoding: 'utf-8',
        env: { ...process.env },
      });
      return { success: true, output: result };
    } catch (error) {
      return { 
        success: false, 
        error: error.message,
        stderr: error.stderr?.toString(),
        stdout: error.stdout?.toString(),
      };
    }
  }

  // Get git status
  fastify.get('/status', async (request, reply) => {
    const { project_id } = request.query;

    if (!project_id) {
      return reply.status(400).send({ 
        error: 'Bad Request', 
        message: 'Project ID is required' 
      });
    }

    const project = db.prepare('SELECT * FROM projects WHERE id = ?').get(project_id);
    
    if (!project) {
      return reply.status(404).send({ error: 'Not Found', message: 'Project not found' });
    }

    if (!fs.existsSync(path.join(project.workspace_path, '.git'))) {
      return reply.status(400).send({ 
        error: 'Bad Request', 
        message: 'Not a git repository. Initialize first.' 
      });
    }

    const status = execGit(project.workspace_path, 'git status --porcelain');
    const branch = execGit(project.workspace_path, 'git branch --show-current');
    const log = execGit(project.workspace_path, 'git log --oneline -5');

    return {
      has_git: true,
      branch: branch.output?.trim(),
      status: status.output?.trim() || 'Working tree clean',
      recent_commits: log.output?.trim().split('\n').filter(l => l),
      is_dirty: !!status.output?.trim(),
    };
  });

  // Initialize git repository
  fastify.post('/init', async (request, reply) => {
    const { project_id } = request.body;

    if (!project_id) {
      return reply.status(400).send({ 
        error: 'Bad Request', 
        message: 'Project ID is required' 
      });
    }

    const project = db.prepare('SELECT * FROM projects WHERE id = ?').get(project_id);
    
    if (!project) {
      return reply.status(404).send({ error: 'Not Found', message: 'Project not found' });
    }

    const result = execGit(project.workspace_path, 'git init');

    if (result.success) {
      logAudit(request.user.userId, 'GIT_INIT', 'project', project_id, {}, request.ip);
    }

    return result;
  });

  // Git commit
  fastify.post('/commit', async (request, reply) => {
    const { project_id, message, files = [] } = request.body;

    if (!project_id || !message) {
      return reply.status(400).send({ 
        error: 'Bad Request', 
        message: 'Project ID and commit message are required' 
      });
    }

    const project = db.prepare('SELECT * FROM projects WHERE id = ?').get(project_id);
    
    if (!project) {
      return reply.status(404).send({ error: 'Not Found', message: 'Project not found' });
    }

    // Stage specific files or all changes
    if (files.length > 0) {
      for (const file of files) {
        execGit(project.workspace_path, `git add "${file}"`);
      }
    } else {
      execGit(project.workspace_path, 'git add -A');
    }

    const commitResult = execGit(project.workspace_path, `git commit -m "${message.replace(/"/g, '\\"')}"`);

    if (commitResult.success) {
      logAudit(request.user.userId, 'GIT_COMMIT', 'project', project_id, { message }, request.ip);
      
      const lastCommit = execGit(project.workspace_path, 'git log -1 --format="%H|%s|%an|%ae|%ai"');
      
      return {
        ...commitResult,
        commit: lastCommit.output?.trim(),
      };
    }

    return commitResult;
  });

  // Git push
  fastify.post('/push', async (request, reply) => {
    const { project_id, remote = 'origin', branch } = request.body;

    if (!project_id) {
      return reply.status(400).send({ 
        error: 'Bad Request', 
        message: 'Project ID is required' 
      });
    }

    const project = db.prepare('SELECT * FROM projects WHERE id = ?').get(project_id);
    
    if (!project) {
      return reply.status(404).send({ error: 'Not Found', message: 'Project not found' });
    }

    const currentBranch = branch || execGit(project.workspace_path, 'git branch --show-current').output?.trim();

    const pushCommand = branch 
      ? `git push ${remote} ${branch}`
      : `git push ${remote}`;

    const result = execGit(project.workspace_path, pushCommand);

    if (result.success) {
      logAudit(request.user.userId, 'GIT_PUSH', 'project', project_id, { remote, branch: currentBranch }, request.ip);
    }

    return result;
  });

  // Git pull
  fastify.post('/pull', async (request, reply) => {
    const { project_id, remote = 'origin', branch } = request.body;

    if (!project_id) {
      return reply.status(400).send({ 
        error: 'Bad Request', 
        message: 'Project ID is required' 
      });
    }

    const project = db.prepare('SELECT * FROM projects WHERE id = ?').get(project_id);
    
    if (!project) {
      return reply.status(404).send({ error: 'Not Found', message: 'Project not found' });
    }

    const pullCommand = branch 
      ? `git pull ${remote} ${branch}`
      : `git pull ${remote}`;

    const result = execGit(project.workspace_path, pullCommand);

    if (result.success) {
      logAudit(request.user.userId, 'GIT_PULL', 'project', project_id, { remote, branch }, request.ip);
    }

    return result;
  });

  // List branches
  fastify.get('/branches', async (request, reply) => {
    const { project_id } = request.query;

    if (!project_id) {
      return reply.status(400).send({ 
        error: 'Bad Request', 
        message: 'Project ID is required' 
      });
    }

    const project = db.prepare('SELECT * FROM projects WHERE id = ?').get(project_id);
    
    if (!project) {
      return reply.status(404).send({ error: 'Not Found', message: 'Project not found' });
    }

    const localBranches = execGit(project.workspace_path, 'git branch');
    const remoteBranches = execGit(project.workspace_path, 'git branch -r');

    return {
      local: localBranches.output?.trim().split('\n').map(b => b.replace('* ', '').trim()).filter(b => b),
      remote: remoteBranches.output?.trim().split('\n').map(b => b.trim()).filter(b => b),
    };
  });

  // Create branch
  fastify.post('/branch', async (request, reply) => {
    const { project_id, name, from = 'HEAD' } = request.body;

    if (!project_id || !name) {
      return reply.status(400).send({ 
        error: 'Bad Request', 
        message: 'Project ID and branch name are required' 
      });
    }

    const project = db.prepare('SELECT * FROM projects WHERE id = ?').get(project_id);
    
    if (!project) {
      return reply.status(404).send({ error: 'Not Found', message: 'Project not found' });
    }

    const result = execGit(project.workspace_path, `git checkout -b ${name} ${from}`);

    if (result.success) {
      logAudit(request.user.userId, 'GIT_BRANCH', 'project', project_id, { name, from }, request.ip);
    }

    return result;
  });

  // Merge branch
  fastify.post('/merge', async (request, reply) => {
    const { project_id, branch } = request.body;

    if (!project_id || !branch) {
      return reply.status(400).send({ 
        error: 'Bad Request', 
        message: 'Project ID and branch name are required' 
      });
    }

    const project = db.prepare('SELECT * FROM projects WHERE id = ?').get(project_id);
    
    if (!project) {
      return reply.status(404).send({ error: 'Not Found', message: 'Project not found' });
    }

    const result = execGit(project.workspace_path, `git merge ${branch}`);

    if (result.success) {
      logAudit(request.user.userId, 'GIT_MERGE', 'project', project_id, { branch }, request.ip);
    }

    return result;
  });

  // Git diff
  fastify.get('/diff', async (request, reply) => {
    const { project_id, file } = request.query;

    if (!project_id) {
      return reply.status(400).send({ 
        error: 'Bad Request', 
        message: 'Project ID is required' 
      });
    }

    const project = db.prepare('SELECT * FROM projects WHERE id = ?').get(project_id);
    
    if (!project) {
      return reply.status(404).send({ error: 'Not Found', message: 'Project not found' });
    }

    const diffCommand = file 
      ? `git diff HEAD -- "${file}"`
      : 'git diff HEAD';

    const result = execGit(project.workspace_path, diffCommand);

    return {
      diff: result.output || '',
      has_changes: !!result.output?.trim(),
    };
  });

  // Git log
  fastify.get('/log', async (request, reply) => {
    const { project_id, limit = 20 } = request.query;

    if (!project_id) {
      return reply.status(400).send({ 
        error: 'Bad Request', 
        message: 'Project ID is required' 
      });
    }

    const project = db.prepare('SELECT * FROM projects WHERE id = ?').get(project_id);
    
    if (!project) {
      return reply.status(404).send({ error: 'Not Found', message: 'Project not found' });
    }

    const result = execGit(project.workspace_path, `git log -${limit} --format="%H|%s|%an|%ae|%ai"`);

    const commits = result.output?.trim().split('\n').map(line => {
      const [hash, message, author, email, date] = line.split('|');
      return { hash, message, author, email, date };
    }).filter(c => c.hash);

    return { commits };
  });
}

export default fastifyPlugin(gitRoutes);
