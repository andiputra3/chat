import fastify from 'fastify';
import cors from '@fastify/cors';
import jwt from '@fastify/jwt';
import websocket from '@fastify/websocket';
import path from 'path';
import { fileURLToPath } from 'url';
import config from '../config/index.js';
import { initializeDatabase, seedDefaultUser } from './db/index.js';
import authRoutes from './routes/auth.js';
import projectRoutes from './routes/projects.js';
import sessionRoutes from './routes/sessions.js';
import chatRoutes from './routes/chat.js';
import fileRoutes from './routes/files.js';
import gitRoutes from './routes/git.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function buildServer() {
  const server = fastify({
    logger: {
      level: config.logLevel,
    },
  });

  // Register plugins
  await server.register(cors, {
    origin: true,
    credentials: true,
  });

  await server.register(jwt, {
    secret: config.jwtSecret,
    sign: {
      expiresIn: config.jwtExpiresIn,
    },
  });

  await server.register(websocket);

  // Initialize database
  await initializeDatabase();
  await seedDefaultUser();

  // Register routes
  await server.register(authRoutes, { prefix: '/api/auth' });
  await server.register(projectRoutes, { prefix: '/api/projects' });
  await server.register(sessionRoutes, { prefix: '/api/sessions' });
  await server.register(chatRoutes, { prefix: '/api/chat' });
  await server.register(fileRoutes, { prefix: '/api/files' });
  await server.register(gitRoutes, { prefix: '/api/git' });

  // Health check endpoint
  server.get('/api/health', async (request, reply) => {
    return { status: 'ok', timestamp: new Date().toISOString() };
  });

  // Error handler
  server.setErrorHandler((error, request, reply) => {
    server.log.error(error);
    
    if (error.validation) {
      reply.status(400).send({
        error: 'Bad Request',
        message: error.message,
      });
    } else if (error.statusCode === 404) {
      reply.status(404).send({
        error: 'Not Found',
        message: 'Route not found',
      });
    } else {
      reply.status(500).send({
        error: 'Internal Server Error',
        message: error.message || 'An unexpected error occurred',
      });
    }
  });

  return server;
}

// Start server
const start = async () => {
  try {
    const server = await buildServer();
    
    await server.listen({
      port: config.port,
      host: config.host,
    });
    
    console.log(`🚀 Server running at http://${config.host}:${config.port}`);
    console.log(`📁 Workspace root: ${config.workspaceRoot}`);
    console.log(`🗄️  Database: ${config.databasePath}`);
  } catch (err) {
    console.error('Failed to start server:', err);
    process.exit(1);
  }
};

start();
