import fastifyPlugin from 'fastify-plugin';
import fs from 'fs';
import path from 'path';
import db, { logAudit } from '../db/index.js';
import config from '../../config/index.js';

async function fileRoutes(fastify, options) {
  // Auth guard for all routes
  fastify.addHook('preHandler', async (request, reply) => {
    try {
      await request.jwtVerify();
    } catch (err) {
      reply.code(401).send({ error: 'Unauthorized', message: 'Invalid token' });
    }
  });

  // List files (tree structure)
  fastify.get('/tree', async (request, reply) => {
    const { project_id, root = '' } = request.query;

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

    const targetPath = path.join(project.workspace_path, root || '');

    if (!fs.existsSync(targetPath)) {
      return reply.status(404).send({ error: 'Not Found', message: 'Path not found' });
    }

    function buildTree(dirPath, relativePath = '') {
      const items = fs.readdirSync(dirPath, { withFileTypes: true });
      
      return items
        .filter(item => !item.name.startsWith('.')) // Skip hidden files
        .map(item => {
          const fullPath = path.join(dirPath, item.name);
          const itemRelativePath = path.join(relativePath, item.name);
          
          if (item.isDirectory()) {
            return {
              name: item.name,
              path: itemRelativePath,
              type: 'directory',
              children: buildTree(fullPath, itemRelativePath),
            };
          } else {
            const stats = fs.statSync(fullPath);
            return {
              name: item.name,
              path: itemRelativePath,
              type: 'file',
              size: stats.size,
              modified: stats.mtime,
            };
          }
        });
    }

    const tree = buildTree(targetPath, root || '');
    return { path: root || project.workspace_path, children: tree };
  });

  // Get file content
  fastify.get('/content', async (request, reply) => {
    const { project_id, file_path } = request.query;

    if (!project_id || !file_path) {
      return reply.status(400).send({ 
        error: 'Bad Request', 
        message: 'Project ID and file path are required' 
      });
    }

    const project = db.prepare('SELECT * FROM projects WHERE id = ?').get(project_id);
    
    if (!project) {
      return reply.status(404).send({ error: 'Not Found', message: 'Project not found' });
    }

    const fullPath = path.join(project.workspace_path, file_path);

    if (!fs.existsSync(fullPath)) {
      return reply.status(404).send({ error: 'Not Found', message: 'File not found' });
    }

    const content = fs.readFileSync(fullPath, 'utf-8');
    const stats = fs.statSync(fullPath);

    return {
      path: file_path,
      content,
      size: stats.size,
      modified: stats.mtime,
      created: stats.birthtime,
    };
  });

  // Create file or directory
  fastify.post('/', async (request, reply) => {
    try {
      const { project_id, path: filePath, type = 'file', content = '' } = request.body;

      if (!project_id || !filePath) {
        return reply.status(400).send({ 
          error: 'Bad Request', 
          message: 'Project ID and path are required' 
        });
      }

      const project = db.prepare('SELECT * FROM projects WHERE id = ?').get(project_id);
      
      if (!project) {
        return reply.status(404).send({ error: 'Not Found', message: 'Project not found' });
      }

      const fullPath = path.join(project.workspace_path, filePath);

      // Check if already exists
      if (fs.existsSync(fullPath)) {
        return reply.status(409).send({ 
          error: 'Conflict', 
          message: 'File or directory already exists' 
        });
      }

      if (type === 'directory') {
        fs.mkdirSync(fullPath, { recursive: true });
        
        logAudit(request.user.userId, 'CREATE_DIR', 'file', null, { 
          project_id, 
          path: filePath 
        }, request.ip);
        
        return { 
          message: 'Directory created successfully',
          path: filePath,
          type: 'directory',
        };
      } else {
        // Ensure parent directory exists
        const dir = path.dirname(fullPath);
        if (!fs.existsSync(dir)) {
          fs.mkdirSync(dir, { recursive: true });
        }

        fs.writeFileSync(fullPath, content, 'utf-8');
        
        logAudit(request.user.userId, 'CREATE', 'file', null, { 
          project_id, 
          path: filePath 
        }, request.ip);
        
        return { 
          message: 'File created successfully',
          path: filePath,
          type: 'file',
        };
      }
    } catch (error) {
      fastify.log.error(error);
      throw error;
    }
  });

  // Update file content
  fastify.put('/', async (request, reply) => {
    try {
      const { project_id, path: filePath, content } = request.body;

      if (!project_id || !filePath || content === undefined) {
        return reply.status(400).send({ 
          error: 'Bad Request', 
          message: 'Project ID, path, and content are required' 
        });
      }

      const project = db.prepare('SELECT * FROM projects WHERE id = ?').get(project_id);
      
      if (!project) {
        return reply.status(404).send({ error: 'Not Found', message: 'Project not found' });
      }

      const fullPath = path.join(project.workspace_path, filePath);

      if (!fs.existsSync(fullPath)) {
        return reply.status(404).send({ error: 'Not Found', message: 'File not found' });
      }

      fs.writeFileSync(fullPath, content, 'utf-8');
      
      logAudit(request.user.userId, 'UPDATE', 'file', null, { 
        project_id, 
        path: filePath 
      }, request.ip);
      
      const stats = fs.statSync(fullPath);
      
      return { 
        message: 'File updated successfully',
        path: filePath,
        size: stats.size,
        modified: stats.mtime,
      };
    } catch (error) {
      fastify.log.error(error);
      throw error;
    }
  });

  // Delete file or directory
  fastify.delete('/', async (request, reply) => {
    const { project_id, path: filePath } = request.query;

    if (!project_id || !filePath) {
      return reply.status(400).send({ 
        error: 'Bad Request', 
        message: 'Project ID and path are required' 
      });
    }

    const project = db.prepare('SELECT * FROM projects WHERE id = ?').get(project_id);
    
    if (!project) {
      return reply.status(404).send({ error: 'Not Found', message: 'Project not found' });
    }

    const fullPath = path.join(project.workspace_path, filePath);

    if (!fs.existsSync(fullPath)) {
      return reply.status(404).send({ error: 'Not Found', message: 'File not found' });
    }

    const stats = fs.statSync(fullPath);
    
    if (stats.isDirectory()) {
      fs.rmSync(fullPath, { recursive: true });
    } else {
      fs.unlinkSync(fullPath);
    }
    
    logAudit(request.user.userId, 'DELETE', 'file', null, { 
      project_id, 
      path: filePath 
    }, request.ip);
    
    return { message: 'Deleted successfully' };
  });

  // Rename file or directory
  fastify.put('/rename', async (request, reply) => {
    try {
      const { project_id, path: oldPath, newPath } = request.body;

      if (!project_id || !oldPath || !newPath) {
        return reply.status(400).send({ 
          error: 'Bad Request', 
          message: 'Project ID, old path, and new path are required' 
        });
      }

      const project = db.prepare('SELECT * FROM projects WHERE id = ?').get(project_id);
      
      if (!project) {
        return reply.status(404).send({ error: 'Not Found', message: 'Project not found' });
      }

      const oldFullPath = path.join(project.workspace_path, oldPath);
      const newFullPath = path.join(project.workspace_path, newPath);

      if (!fs.existsSync(oldFullPath)) {
        return reply.status(404).send({ error: 'Not Found', message: 'Source not found' });
      }

      if (fs.existsSync(newFullPath)) {
        return reply.status(409).send({ 
          error: 'Conflict', 
          message: 'Destination already exists' 
        });
      }

      fs.renameSync(oldFullPath, newFullPath);
      
      logAudit(request.user.userId, 'RENAME', 'file', null, { 
        project_id, 
        oldPath, 
        newPath 
      }, request.ip);
      
      return { 
        message: 'Renamed successfully',
        oldPath,
        newPath,
      };
    } catch (error) {
      fastify.log.error(error);
      throw error;
    }
  });

  // Upload file
  fastify.post('/upload', async (request, reply) => {
    // This would need multipart/form-data handling
    // For simplicity, we'll return a placeholder
    return { 
      message: 'File upload endpoint - implement with @fastify/multipart',
      note: 'Use FormData to upload files with binary content',
    };
  });

  // Download file
  fastify.get('/download', async (request, reply) => {
    const { project_id, path: filePath } = request.query;

    if (!project_id || !filePath) {
      return reply.status(400).send({ 
        error: 'Bad Request', 
        message: 'Project ID and path are required' 
      });
    }

    const project = db.prepare('SELECT * FROM projects WHERE id = ?').get(project_id);
    
    if (!project) {
      return reply.status(404).send({ error: 'Not Found', message: 'Project not found' });
    }

    const fullPath = path.join(project.workspace_path, filePath);

    if (!fs.existsSync(fullPath)) {
      return reply.status(404).send({ error: 'Not Found', message: 'File not found' });
    }

    const stats = fs.statSync(fullPath);
    
    if (stats.isDirectory()) {
      return reply.status(400).send({ 
        error: 'Bad Request', 
        message: 'Cannot download directories' 
      });
    }

    return reply.sendFile(filePath, project.workspace_path);
  });
}

export default fastifyPlugin(fileRoutes);
