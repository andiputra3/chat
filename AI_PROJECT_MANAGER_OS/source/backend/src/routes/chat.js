import fastifyPlugin from 'fastify-plugin';
import db, { logAudit } from '../db/index.js';

async function chatRoutes(fastify, options) {
  // Auth guard for all routes
  fastify.addHook('preHandler', async (request, reply) => {
    try {
      await request.jwtVerify();
    } catch (err) {
      reply.code(401).send({ error: 'Unauthorized', message: 'Invalid token' });
    }
  });

  // Send message (with streaming support via WebSocket)
  fastify.post('/', {
    websocket: true,
  }, async (connection, req) => {
    const session = await req.server.db.prepare('SELECT * FROM sessions WHERE id = ?').get(req.query.sessionId);
    
    if (!session) {
      connection.socket.send(JSON.stringify({ error: 'Session not found' }));
      connection.socket.close();
      return;
    }

    // Handle incoming messages
    connection.socket.on('message', async (data) => {
      try {
        const message = JSON.parse(data.toString());
        
        if (message.type === 'user_message') {
          // Save user message to database
          const insert = req.server.db.prepare(`
            INSERT INTO messages (session_id, role, content, token_count)
            VALUES (?, 'user', ?, ?)
          `);
          
          const tokenCount = Math.ceil(message.content.length / 4); // Rough estimate
          insert.run(session.id, message.content, tokenCount);
          
          // Update session token count
          req.server.db.prepare(`
            UPDATE sessions SET token_count = token_count + ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
          `).run(tokenCount, session.id);
          
          // Acknowledge receipt
          connection.socket.send(JSON.stringify({ 
            type: 'ack', 
            messageId: 'user_' + Date.now() 
          }));
          
          // In a real implementation, this would call the AI service
          // For now, we'll send a placeholder response
          connection.socket.send(JSON.stringify({
            type: 'assistant_start',
          }));
          
          // Simulate streaming response
          const response = "This is a placeholder response. In production, this would stream from Claude Code/OpenCode.";
          const chunks = response.split(' ');
          
          for (const chunk of chunks) {
            connection.socket.send(JSON.stringify({
              type: 'assistant_chunk',
              content: chunk + ' ',
            }));
            await new Promise(resolve => setTimeout(resolve, 100));
          }
          
          connection.socket.send(JSON.stringify({
            type: 'assistant_complete',
          }));
          
          // Save complete response to database
          const aiTokenCount = Math.ceil(response.length / 4);
          req.server.db.prepare(`
            INSERT INTO messages (session_id, role, content, token_count)
            VALUES (?, 'assistant', ?, ?)
          `).run(session.id, response, aiTokenCount);
          
          req.server.db.prepare(`
            UPDATE sessions SET token_count = token_count + ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
          `).run(aiTokenCount, session.id);
          
        } else if (message.type === 'stop') {
          // Stop generation (would need to implement cancellation logic)
          connection.socket.send(JSON.stringify({
            type: 'stopped',
          }));
        }
      } catch (error) {
        connection.socket.send(JSON.stringify({
          error: error.message,
        }));
      }
    });
  });

  // HTTP endpoint for non-streaming chat (fallback)
  fastify.post('/send', async (request, reply) => {
    try {
      const { session_id, content } = request.body;

      if (!session_id || !content) {
        return reply.status(400).send({ 
          error: 'Bad Request', 
          message: 'Session ID and content are required' 
        });
      }

      // Verify session exists
      const session = db.prepare('SELECT * FROM sessions WHERE id = ?').get(session_id);
      
      if (!session) {
        return reply.status(404).send({ error: 'Not Found', message: 'Session not found' });
      }

      // Save user message
      const userTokenCount = Math.ceil(content.length / 4);
      const insertUser = db.prepare(`
        INSERT INTO messages (session_id, role, content, token_count)
        VALUES (?, 'user', ?, ?)
      `);
      insertUser.run(session_id, content, userTokenCount);

      // Update session token count
      db.prepare(`
        UPDATE sessions SET token_count = token_count + ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
      `).run(userTokenCount, session_id);

      // In production, this would call AI service
      // For now, return a placeholder response
      const aiResponse = "This is a placeholder response. In production, integrate with Claude Code or OpenCode API.";
      const aiTokenCount = Math.ceil(aiResponse.length / 4);

      // Save AI response
      const insertAI = db.prepare(`
        INSERT INTO messages (session_id, role, content, token_count)
        VALUES (?, 'assistant', ?, ?)
      `);
      insertAI.run(session_id, aiResponse, aiTokenCount);

      // Update session token count
      db.prepare(`
        UPDATE sessions SET token_count = token_count + ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
      `).run(aiTokenCount, session_id);

      logAudit(request.user.userId, 'CHAT', 'session', session_id, { 
        message_length: content.length 
      }, request.ip);

      return {
        user_message: {
          role: 'user',
          content,
          token_count: userTokenCount,
        },
        assistant_message: {
          role: 'assistant',
          content: aiResponse,
          token_count: aiTokenCount,
        },
        total_tokens: session.token_count + userTokenCount + aiTokenCount,
      };
    } catch (error) {
      fastify.log.error(error);
      throw error;
    }
  });

  // Get chat history
  fastify.get('/history/:sessionId', async (request, reply) => {
    const { sessionId } = request.params;
    const { page = 1, limit = 50 } = request.query;

    const offset = (page - 1) * limit;

    const messages = db.prepare(`
      SELECT * FROM messages 
      WHERE session_id = ? 
      ORDER BY created_at ASC
      LIMIT ? OFFSET ?
    `).all(sessionId, parseInt(limit), parseInt(offset));

    const total = db.prepare('SELECT COUNT(*) as count FROM messages WHERE session_id = ?').get(sessionId);

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

  // Retry last message
  fastify.post('/retry', async (request, reply) => {
    const { session_id } = request.body;

    // Get last user message
    const lastUserMessage = db.prepare(`
      SELECT * FROM messages 
      WHERE session_id = ? AND role = 'user' 
      ORDER BY created_at DESC 
      LIMIT 1
    `).get(session_id);

    if (!lastUserMessage) {
      return reply.status(404).send({ 
        error: 'Not Found', 
        message: 'No user message to retry' 
      });
    }

    // Delete last assistant message if exists
    db.prepare(`
      DELETE FROM messages 
      WHERE session_id = ? AND role = 'assistant' 
      AND created_at > ?
    `).run(session_id, lastUserMessage.created_at);

    // Re-generate response (in production, call AI service)
    const aiResponse = "Retried response placeholder.";
    const aiTokenCount = Math.ceil(aiResponse.length / 4);

    db.prepare(`
      INSERT INTO messages (session_id, role, content, token_count)
      VALUES (?, 'assistant', ?, ?)
    `).run(session_id, aiResponse, aiTokenCount);

    logAudit(request.user.userId, 'RETRY', 'session', session_id, {}, request.ip);

    return {
      role: 'assistant',
      content: aiResponse,
      token_count: aiTokenCount,
    };
  });

  // Export chat
  fastify.post('/export', async (request, reply) => {
    const { session_id, format = 'markdown' } = request.body;

    const messages = db.prepare(`
      SELECT * FROM messages 
      WHERE session_id = ? 
      ORDER BY created_at ASC
    `).all(session_id);

    if (messages.length === 0) {
      return reply.status(404).send({ 
        error: 'Not Found', 
        message: 'No messages to export' 
      });
    }

    let exportedContent = '';

    if (format === 'markdown') {
      exportedContent = '# Chat Export\n\n';
      messages.forEach(msg => {
        const prefix = msg.role === 'user' ? '👤 User' : '🤖 Assistant';
        exportedContent += `## ${prefix}\n\n${msg.content}\n\n`;
      });
    } else if (format === 'json') {
      exportedContent = JSON.stringify(messages, null, 2);
    }

    return {
      format,
      content: exportedContent,
      message_count: messages.length,
    };
  });
}

export default fastifyPlugin(chatRoutes);
