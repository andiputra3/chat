import fastifyPlugin from 'fastify-plugin';
import { v4 as uuidv4 } from 'uuid';
import path from 'path';
import fs from 'fs';
import db, { logAudit } from '../db/index.js';
import config from '../../config/index.js';

async function projectRoutes(fastify, options) {
  // Auth guard for all routes
  fastify.addHook('preHandler', async (request, reply) => {
    try {
      await request.jwtVerify();
    } catch (err) {
      reply.code(401).send({ error: 'Unauthorized', message: 'Invalid token' });
    }
  });

  // List all projects
  fastify.get('/', async (request, reply) => {
    const projects = db.prepare(`
      SELECT p.*, u.username as created_by_username
      FROM projects p
      LEFT JOIN users u ON p.created_by = u.id
      WHERE p.status != 'deleted'
      ORDER BY p.created_at DESC
    `).all();

    return projects;
  });

  // Get single project
  fastify.get('/:id', async (request, reply) => {
    const { id } = request.params;
    
    const project = db.prepare(`
      SELECT p.*, u.username as created_by_username
      FROM projects p
      LEFT JOIN users u ON p.created_by = u.id
      WHERE p.id = ? AND p.status != 'deleted'
    `).get(id);

    if (!project) {
      return reply.status(404).send({ error: 'Not Found', message: 'Project not found' });
    }

    return project;
  });

  // Create new project
  fastify.post('/', async (request, reply) => {
    try {
      const { name, description } = request.body;

      if (!name) {
        return reply.status(400).send({ error: 'Bad Request', message: 'Project name is required' });
      }

      // Create workspace directory
      const workspacePath = path.join(config.workspaceRoot, name.toLowerCase().replace(/[^a-z0-9]/g, '_'));
      
      if (!fs.existsSync(workspacePath)) {
        fs.mkdirSync(workspacePath, { recursive: true });
        
        // Create standard folder structure
        const folders = ['chat', 'docs', 'src', 'artifacts', 'pipeline'];
        folders.forEach(folder => {
          fs.mkdirSync(path.join(workspacePath, folder), { recursive: true });
        });
      }

      const insert = db.prepare(`
        INSERT INTO projects (name, description, workspace_path, status, created_by)
        VALUES (?, ?, ?, 'active', ?)
      `);

      const result = insert.run(name, description || '', workspacePath, request.user.userId);

      logAudit(request.user.userId, 'CREATE', 'project', result.lastInsertRowid, { name }, request.ip);

      return {
        id: result.lastInsertRowid,
        name,
        description,
        workspace_path: workspacePath,
        status: 'active',
        created_at: new Date().toISOString(),
      };
    } catch (error) {
      fastify.log.error(error);
      throw error;
    }
  });

  // Update project
  fastify.put('/:id', async (request, reply) => {
    const { id } = request.params;
    const { name, description, status } = request.body;

    const project = db.prepare('SELECT * FROM projects WHERE id = ?').get(id);

    if (!project) {
      return reply.status(404).send({ error: 'Not Found', message: 'Project not found' });
    }

    const update = db.prepare(`
      UPDATE projects 
      SET name = COALESCE(?, name),
          description = COALESCE(?, description),
          status = COALESCE(?, status),
          updated_at = CURRENT_TIMESTAMP
      WHERE id = ?
    `);

    update.run(name, description, status, id);

    logAudit(request.user.userId, 'UPDATE', 'project', id, { name, description, status }, request.ip);

    return db.prepare('SELECT * FROM projects WHERE id = ?').get(id);
  });

  // Delete project (soft delete)
  fastify.delete('/:id', async (request, reply) => {
    const { id } = request.params;

    const project = db.prepare('SELECT * FROM projects WHERE id = ?').get(id);

    if (!project) {
      return reply.status(404).send({ error: 'Not Found', message: 'Project not found' });
    }

    db.prepare("UPDATE projects SET status = 'deleted', updated_at = CURRENT_TIMESTAMP WHERE id = ?").run(id);

    logAudit(request.user.userId, 'DELETE', 'project', id, { name: project.name }, request.ip);

    return { message: 'Project deleted successfully' };
  });

  // Clone project
  fastify.post('/:id/clone', async (request, reply) => {
    const { id } = request.params;
    const { newName } = request.body;

    const sourceProject = db.prepare('SELECT * FROM projects WHERE id = ?').get(id);

    if (!sourceProject) {
      return reply.status(404).send({ error: 'Not Found', message: 'Source project not found' });
    }

    const cloneName = newName || `${sourceProject.name} (Copy)`;
    const cloneWorkspacePath = path.join(config.workspaceRoot, cloneName.toLowerCase().replace(/[^a-z0-9]/g, '_'));

    // Copy workspace files
    if (fs.existsSync(sourceProject.workspace_path)) {
      fs.cpSync(sourceProject.workspace_path, cloneWorkspacePath, { recursive: true });
    }

    const insert = db.prepare(`
      INSERT INTO projects (name, description, workspace_path, constitution_path, status, created_by)
      VALUES (?, ?, ?, ?, 'active', ?)
    `);

    const result = insert.run(
      cloneName,
      sourceProject.description,
      cloneWorkspacePath,
      sourceProject.constitution_path,
      request.user.userId
    );

    logAudit(request.user.userId, 'CLONE', 'project', result.lastInsertRowid, { 
      sourceId: id, 
      sourceName: sourceProject.name,
      cloneName 
    }, request.ip);

    return {
      id: result.lastInsertRowid,
      name: cloneName,
      workspace_path: cloneWorkspacePath,
      message: 'Project cloned successfully',
    };
  });

  // Archive project
  fastify.post('/:id/archive', async (request, reply) => {
    const { id } = request.params;

    const project = db.prepare('SELECT * FROM projects WHERE id = ?').get(id);

    if (!project) {
      return reply.status(404).send({ error: 'Not Found', message: 'Project not found' });
    }

    db.prepare("UPDATE projects SET status = 'archived', updated_at = CURRENT_TIMESTAMP WHERE id = ?").run(id);

    logAudit(request.user.userId, 'ARCHIVE', 'project', id, { name: project.name }, request.ip);

    return { message: 'Project archived successfully' };
  });

  // Restore project
  fastify.post('/:id/restore', async (request, reply) => {
    const { id } = request.params;

    const project = db.prepare('SELECT * FROM projects WHERE id = ?').get(id);

    if (!project) {
      return reply.status(404).send({ error: 'Not Found', message: 'Project not found' });
    }

    db.prepare("UPDATE projects SET status = 'active', updated_at = CURRENT_TIMESTAMP WHERE id = ?").run(id);

    logAudit(request.user.userId, 'RESTORE', 'project', id, { name: project.name }, request.ip);

    return { message: 'Project restored successfully' };
  });
}

export default fastifyPlugin(projectRoutes);
