# AI Project Manager OS

A comprehensive project management system integrated with Claude Code/OpenCode running on VPS.

## Architecture

```
┌─────────────────────────────────────────┐
│         LAYER 1: PROJECT MANAGER        │
│   (Dashboard + Backend API + Session)   │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│         LAYER 2: PROJECT FACTORY        │
│  (Specification + Artifact Generator)   │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│         LAYER 3: PROJECT BUILDER        │
│    (AI Code Gen + Testing + Deploy)     │
└─────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Node.js 20+
- npm or yarn
- Git

### Installation

#### Backend

```bash
cd source/backend
npm install
cp .env.example .env
# Edit .env with your configuration
npm run dev
```

The backend will start on `http://localhost:3001`

#### Frontend

```bash
cd source/frontend
npm install
npm run dev
```

The frontend will start on `http://localhost:3002`

### Default Credentials

- Username: `admin`
- Password: `admin123`

## Features

### Project Management
- Create, edit, delete projects
- Clone projects
- Archive/restore projects
- Workspace management

### Session Management
- Multiple chat sessions per project
- Session summaries
- Token usage tracking
- Context isolation

### Chat Interface
- Real-time messaging with AI
- Streaming responses
- Markdown support
- Code highlighting
- Export conversations

### File Management
- Tree view file explorer
- Create, edit, delete files
- Upload/download files
- Syntax highlighting

### Git Integration
- Initialize repositories
- Commit changes
- Push/Pull
- Branch management
- View history and diffs

### Security
- JWT authentication
- Role-based access control
- Audit logging
- Input validation

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user

### Projects
- `GET /api/projects` - List all projects
- `POST /api/projects` - Create project
- `GET /api/projects/:id` - Get project details
- `PUT /api/projects/:id` - Update project
- `DELETE /api/projects/:id` - Delete project
- `POST /api/projects/:id/clone` - Clone project
- `POST /api/projects/:id/archive` - Archive project
- `POST /api/projects/:id/restore` - Restore project

### Sessions
- `GET /api/sessions/project/:projectId` - List sessions
- `POST /api/sessions` - Create session
- `GET /api/sessions/:id` - Get session details
- `DELETE /api/sessions/:id` - Delete session
- `POST /api/sessions/:id/summary` - Generate summary

### Chat
- `POST /api/chat/send` - Send message
- `GET /api/chat/history/:sessionId` - Get history
- `POST /api/chat/retry` - Retry response
- `POST /api/chat/export` - Export conversation

### Files
- `GET /api/files/tree` - List files
- `GET /api/files/content` - Get file content
- `POST /api/files` - Create file
- `PUT /api/files` - Update file
- `DELETE /api/files` - Delete file

### Git
- `GET /api/git/status` - Git status
- `POST /api/git/init` - Initialize repo
- `POST /api/git/commit` - Commit changes
- `POST /api/git/push` - Push to remote
- `POST /api/git/pull` - Pull from remote

## Configuration

Edit `.env` file in the backend directory:

```env
NODE_ENV=development
PORT=3001
DATABASE_PATH=./data/app.db
JWT_SECRET=your-secret-key
WORKSPACE_ROOT=/workspace
VPS_URL=http://localhost:3000
VPS_API_KEY=your-api-key
```

## Project Structure

```
AI_PROJECT_MANAGER_OS/
├── docs/                      # Documentation
├── source/
│   ├── backend/               # Node.js + Fastify API
│   └── frontend/              # React + Vite Dashboard
├── tests/                     # Test suite
├── scripts/                   # Build scripts
├── config/                    # Configuration
└── workspace/                 # User projects
```

## License

MIT
