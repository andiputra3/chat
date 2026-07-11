import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load environment variables
dotenv.config({ path: path.join(__dirname, '../../.env') });

export default {
  // Server
  nodeEnv: process.env.NODE_ENV || 'development',
  port: parseInt(process.env.PORT) || 3001,
  host: process.env.HOST || '0.0.0.0',

  // Database
  databasePath: process.env.DATABASE_PATH || './data/app.db',

  // JWT
  jwtSecret: process.env.JWT_SECRET || 'default-secret-change-me',
  jwtExpiresIn: process.env.JWT_EXPIRES_IN || '15m',
  jwtRefreshExpiresIn: process.env.JWT_REFRESH_EXPIRES_IN || '7d',

  // VPS/AI
  vpsUrl: process.env.VPS_URL || 'http://localhost:3000',
  vpsApiKey: process.env.VPS_API_KEY || '',
  vpsTimeout: parseInt(process.env.VPS_TIMEOUT) || 300,

  // Workspace
  workspaceRoot: process.env.WORKSPACE_ROOT || '/workspace',

  // Logging
  logLevel: process.env.LOG_LEVEL || 'info',
  logFile: process.env.LOG_FILE || './logs/app.log',

  // Security
  rateLimitMax: parseInt(process.env.RATE_LIMIT_MAX) || 100,
  rateLimitWindow: parseInt(process.env.RATE_LIMIT_WINDOW) || 60000,
};
