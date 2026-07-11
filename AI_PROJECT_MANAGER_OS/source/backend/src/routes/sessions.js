import fastifyPlugin from 'fastify-plugin';
import fs from 'fs';
import path from 'path';
import db, { logAudit } from '../db/index.js';

async function sessionRoutes(fastify, options) {
  // Auth guard for all routes
  fastify.addHook('preHandler', async (request, reply) => {
    try {
      await request.jwtVerify();
    } catch (err) {
      reply.code(401).send({ error: 'Unauthorized', message: 'Invalid token' });
    }
  });

  // Get single session - MUST be before /project/:projectId to avoid route conflict
  fastify.get('/:id', async (request, reply) => {
    const { id } = request.params;
    
    const session = db.prepare('SELECT * FROM sessions WHERE id = ?').get(id);

    if (!session) {
      return reply.status(404).send({ error: 'Not Found', message: 'Session not found' });
    }

    // Get messages for this session
    const messages = db.prepare(`
      SELECT * FROM messages 
      WHERE session_id = ? 
      ORDER BY created_at ASC
    `).all(id);

    return {
      ...session,
      messages,
    };
  });

  // List sessions for a project
  fastify.get('/project/:projectId', async (request, reply) => {
    const { projectId } = request.params;
    
    const sessions = db.prepare(`
      SELECT * FROM sessions 
      WHERE project_id = ? 
      ORDER BY created_at DESC
    `).all(projectId);

    return sessions;
  });

  // Create new session
  fastify.post('/', async (request, reply) => {
    try {
      const { project_id, name } = request.body;

      if (!project_id || !name) {
        return reply.status(400).send({ 
          error: 'Bad Request', 
          message: 'Project ID and session name are required' 
        });
      }

      // Verify project exists
      const project = db.prepare('SELECT * FROM projects WHERE id = ?').get(project_id);
      
      if (!project) {
        return reply.status(404).send({ error: 'Not Found', message: 'Project not found' });
      }

      const insert = db.prepare(`
        INSERT INTO sessions (project_id, name, status)
        VALUES (?, ?, 'active')
      `);

      const result = insert.run(project_id, name);

      // Create chat directory in workspace if not exists
      const chatDir = path.join(project.workspace_path, 'chat');
      if (!fs.existsSync(chatDir)) {
        fs.mkdirSync(chatDir, { recursive: true });
      }

      // Initialize session file
      const sessionFile = path.join(chatDir, 'session.json');
      const sessionData = {
        id: result.lastInsertRowid,
        name,
        project_id,
        created_at: new Date().toISOString(),
        messages: [],
        summary: '',
        token_count: 0,
      };
      
      fs.writeFileSync(sessionFile, JSON.stringify(sessionData, null, 2));

      logAudit(request.user.userId, 'CREATE', 'session', result.lastInsertRowid, { 
        name, 
        project_id 
      }, request.ip);

      return {
        id: result.lastInsertRowid,
        name,
        project_id,
        status: 'active',
        created_at: new Date().toISOString(),
      };
    } catch (error) {
      fastify.log.error(error);
      throw error;
    }
  });

  // Update session (e.g., update summary)
  fastify.put('/:id', async (request, reply) => {
    const { id } = request.params;
    const { name, summary, token_count, status } = request.body;

    const session = db.prepare('SELECT * FROM sessions WHERE id = ?').get(id);

    if (!session) {
      return reply.status(404).send({ error: 'Not Found', message: 'Session not found' });
    }

    const update = db.prepare(`
      UPDATE sessions 
      SET name = COALESCE(?, name),
          summary = COALESCE(?, summary),
          token_count = COALESCE(?, token_count),
          status = COALESCE(?, status),
          updated_at = CURRENT_TIMESTAMP
      WHERE id = ?
    `);

    update.run(name, summary, token_count, status, id);

    logAudit(request.user.userId, 'UPDATE', 'session', id, { name, status }, request.ip);

    return db.prepare('SELECT * FROM sessions WHERE id = ?').get(id);
  });

  // Delete session
  fastify.delete('/:id', async (request, reply) => {
    const { id } = request.params;

    const session = db.prepare('SELECT * FROM sessions WHERE id = ?').get(id);

    if (!session) {
      return reply.status(404).send({ error: 'Not Found', message: 'Session not found' });
    }

    // Delete messages first (cascade should handle this, but being explicit)
    db.prepare('DELETE FROM messages WHERE session_id = ?').run(id);
    
    // Delete session
    db.prepare('DELETE FROM sessions WHERE id = ?').run(id);

    logAudit(request.user.userId, 'DELETE', 'session', id, { name: session.name }, request.ip);

    return { message: 'Session deleted successfully' };
  });

  // Generate session summary
  fastify.post('/:id/summary', async (request, reply) => {
    const { id } = request.params;

    const session = db.prepare('SELECT * FROM sessions WHERE id = ?').get(id);

    if (!session) {
      return reply.status(404).send({ error: 'Not Found', message: 'Session not found' });
    }

    // Get all messages for summarization
    const messages = db.prepare(`
      SELECT role, content FROM messages 
      WHERE session_id = ? 
      ORDER BY created_at ASC
    `).all(id);

    if (messages.length === 0) {
      return reply.status(400).send({ 
        error: 'Bad Request', 
        message: 'No messages to summarize' 
      });
    }

    // In a real implementation, this would call AI to generate summary
    // For now, we'll create a simple summary
    const summary = `Session Summary: ${messages.length} messages exchanged.\nGenerated at: ${new Date().toISOString()}`;

    const update = db.prepare('UPDATE sessions SET summary = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?');
    update.run(summary, id);

    // Save summary to file
    const project = db.prepare('SELECT * FROM projects WHERE id = ?').get(session.project_id);
    if (project) {
      const summaryFile = path.join(project.workspace_path, 'chat', 'summary.md');
      fs.writeFileSync(summaryFile, summary);
    }

    logAudit(request.user.userId, 'SUMMARIZE', 'session', id, {}, request.ip);

    return { id, summary };
  });

  // Get session history (for chat display)
  fastify.get('/:id/history', async (request, reply) => {
    const { id } = request.params;
    const { page = 1, limit = 50 } = request.query;

    const offset = (page - 1) * limit;

    const messages = db.prepare(`
      SELECT * FROM messages 
      WHERE session_id = ? 
      ORDER BY created_at ASC
      LIMIT ? OFFSET ?
    `).all(id, parseInt(limit), parseInt(offset));

    const total = db.prepare('SELECT COUNT(*) as count FROM messages WHERE session_id = ?').get(id);

    return {
      messages,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total: total.count,
        totalPages: Math.ceil(total.count / limit),
      },
    };
  });
}

export default fastifyPlugin(sessionRoutes);
