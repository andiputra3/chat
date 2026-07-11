import fastifyPlugin from 'fastify-plugin';
import bcrypt from 'bcryptjs';
import db, { logAudit } from '../db/index.js';

async function authRoutes(fastify, options) {
  // Login
  fastify.post('/login', async (request, reply) => {
    try {
      const { username, password } = request.body;

      if (!username || !password) {
        return reply.status(400).send({ 
          error: 'Bad Request', 
          message: 'Username and password are required' 
        });
      }

      const user = db.prepare('SELECT * FROM users WHERE username = ?').get(username);

      if (!user) {
        return reply.status(401).send({ 
          error: 'Unauthorized', 
          message: 'Invalid credentials' 
        });
      }

      const validPassword = bcrypt.compareSync(password, user.password_hash);

      if (!validPassword) {
        return reply.status(401).send({ 
          error: 'Unauthorized', 
          message: 'Invalid credentials' 
        });
      }

      const accessToken = fastify.jwt.sign({ 
        userId: user.id, 
        username: user.username, 
        role: user.role 
      });

      const refreshToken = fastify.jwt.sign({ 
        userId: user.id 
      }, { expiresIn: '7d' });

      logAudit(user.id, 'LOGIN', 'user', user.id, {}, request.ip);

      return {
        user: {
          id: user.id,
          username: user.username,
          email: user.email,
          role: user.role,
        },
        accessToken,
        refreshToken,
      };
    } catch (error) {
      fastify.log.error(error);
      throw error;
    }
  });

  // Logout
  fastify.post('/logout', async (request, reply) => {
    // In a real app, you might invalidate the token or add it to a blacklist
    return { message: 'Logged out successfully' };
  });

  // Refresh token
  fastify.post('/refresh', async (request, reply) => {
    try {
      const { refreshToken } = request.body;

      if (!refreshToken) {
        return reply.status(400).send({ 
          error: 'Bad Request', 
          message: 'Refresh token is required' 
        });
      }

      const decoded = fastify.jwt.verify(refreshToken);
      
      const user = db.prepare('SELECT * FROM users WHERE id = ?').get(decoded.userId);

      if (!user) {
        return reply.status(401).send({ 
          error: 'Unauthorized', 
          message: 'User not found' 
        });
      }

      const accessToken = fastify.jwt.sign({ 
        userId: user.id, 
        username: user.username, 
        role: user.role 
      });

      return { accessToken };
    } catch (error) {
      return reply.status(401).send({ 
        error: 'Unauthorized', 
        message: 'Invalid refresh token' 
      });
    }
  });

  // Get current user
  fastify.get('/me', {
    preHandler: [async (request, reply) => {
      try {
        await request.jwtVerify();
      } catch (err) {
        reply.code(401).send({ error: 'Unauthorized', message: 'Invalid token' });
      }
    }]
  }, async (request, reply) => {
    const user = db.prepare('SELECT id, username, email, role, created_at FROM users WHERE id = ?').get(request.user.userId);
    
    if (!user) {
      return reply.status(404).send({ error: 'Not Found', message: 'User not found' });
    }

    return user;
  });
}

export default fastifyPlugin(authRoutes);
