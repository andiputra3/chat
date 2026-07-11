# System Architecture - AI Project Manager OS

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                            │
│                    (React + Tailwind CSS)                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LAYER 1: PROJECT MANAGER                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Frontend Dashboard (React + Vite)                         │  │
│  │ - Project List                                            │  │
│  │ - Chat Interface                                          │  │
│  │ - File Explorer                                           │  │
│  │ - Session Manager                                         │  │
│  │ - Git UI                                                  │  │
│  │ - Pipeline Viewer                                         │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              │ REST API / WebSocket              │
│                              ▼                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Backend API (Node.js + Fastify)                           │  │
│  │ - Auth Middleware                                         │  │
│  │ - Project Controller                                      │  │
│  │ - Session Controller                                      │  │
│  │ - Chat Controller                                         │  │
│  │ - File Controller                                         │  │
│  │ - Git Controller                                          │  │
│  │ - Pipeline Controller                                     │  │
│  │ - Artifact Controller                                     │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              │                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Data Layer                                                │  │
│  │ - SQLite Database                                         │  │
│  │ - File System Storage                                     │  │
│  │ - Session Store                                           │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP API / CLI
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LAYER 2: PROJECT FACTORY                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Specification Engine                                      │  │
│  │ - Prompt Builder                                          │  │
│  │ - Context Manager                                         │  │
│  │ - Template Engine                                         │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ▼                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Artifact Generator                                        │  │
│  │ - Document Generator                                      │  │
│  │ - Code Generator                                          │  │
│  │ - Config Generator                                        │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ AI Prompts
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LAYER 3: PROJECT BUILDER                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ AI Runtime (Claude Code / OpenCode)                       │  │
│  │ - CLI Executor                                            │  │
│  │ - Stream Parser                                           │  │
│  │ - Error Handler                                           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ▼                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Build Pipeline                                            │  │
│  │ - Code Generation                                         │  │
│  │ - Testing                                                 │  │
│  │ - Validation                                              │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ▼                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Git Integration                                           │  │
│  │ - Commit                                                  │  │
│  │ - Push/Pull                                               │  │
│  │ - Branch Management                                       │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 2. Component Details

### 2.1 Frontend Dashboard

**Tech Stack:**
- React 18+
- Vite (build tool)
- Tailwind CSS (styling)
- Zustand (state management)
- React Router (navigation)
- react-markdown + remark-gfm (markdown rendering)
- prismjs (code highlighting)
- Socket.IO client (real-time)

**Main Views:**
1. **Dashboard Home** - Project overview, stats, recent activity
2. **Project List** - Create, edit, delete, clone projects
3. **Chat Interface** - Real-time chat with Claude
4. **File Explorer** - Tree view, CRUD operations
5. **Session Manager** - Session list, summary, restore
6. **Git UI** - Commit, push, pull, branch management
7. **Pipeline Viewer** - Pipeline status, logs, controls
8. **Settings** - Configuration, API keys, preferences

### 2.2 Backend API

**Tech Stack:**
- Node.js 20+
- Fastify (web framework)
- Better-SQLite3 (database)
- JWT (authentication)
- WebSocket (real-time)
- PM2 (process manager)

**API Endpoints:**

#### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `POST /api/auth/refresh` - Refresh token

#### Projects
- `GET /api/projects` - List all projects
- `POST /api/projects` - Create new project
- `GET /api/projects/:id` - Get project details
- `PUT /api/projects/:id` - Update project
- `DELETE /api/projects/:id` - Delete project
- `POST /api/projects/:id/clone` - Clone project
- `POST /api/projects/:id/archive` - Archive project
- `POST /api/projects/:id/restore` - Restore project

#### Sessions
- `GET /api/projects/:projectId/sessions` - List sessions
- `POST /api/projects/:projectId/sessions` - Create session
- `GET /api/sessions/:id` - Get session details
- `DELETE /api/sessions/:id` - Delete session
- `POST /api/sessions/:id/summary` - Generate summary
- `POST /api/sessions/:id/restore` - Restore session

#### Chat
- `POST /api/chat` - Send message (streaming)
- `POST /api/chat/stop` - Stop generation
- `POST /api/chat/retry` - Retry last message
- `POST /api/chat/continue` - Continue response
- `GET /api/chat/history` - Get chat history
- `POST /api/chat/export` - Export chat

#### Files
- `GET /api/files` - List files (tree)
- `POST /api/files` - Create file/folder
- `PUT /api/files/:path` - Update file
- `DELETE /api/files/:path` - Delete file
- `POST /api/files/upload` - Upload file
- `GET /api/files/download/:path` - Download file

#### Git
- `GET /api/git/status` - Git status
- `POST /api/git/commit` - Commit changes
- `POST /api/git/push` - Push to remote
- `POST /api/git/pull` - Pull from remote
- `GET /api/git/branches` - List branches
- `POST /api/git/branch` - Create branch
- `POST /api/git/merge` - Merge branches

#### Pipeline
- `GET /api/pipeline` - List pipelines
- `POST /api/pipeline` - Create pipeline
- `POST /api/pipeline/:id/run` - Run pipeline
- `GET /api/pipeline/:id/logs` - Get pipeline logs

### 2.3 Database Schema

```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'developer',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Projects table
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    workspace_path TEXT NOT NULL,
    constitution_path TEXT,
    status TEXT DEFAULT 'active',
    created_by INTEGER REFERENCES users(id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Sessions table
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER REFERENCES projects(id),
    name TEXT NOT NULL,
    summary TEXT,
    token_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Messages table
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER REFERENCES sessions(id),
    role TEXT NOT NULL, -- 'user' or 'assistant'
    content TEXT NOT NULL,
    token_count INTEGER,
    metadata JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Artifacts table
CREATE TABLE artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER REFERENCES projects(id),
    session_id INTEGER REFERENCES sessions(id),
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    path TEXT NOT NULL,
    content_hash TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Pipelines table
CREATE TABLE pipelines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER REFERENCES projects(id),
    name TEXT NOT NULL,
    stages JSON NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME
);

-- Audit Logs table
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    action TEXT NOT NULL,
    resource_type TEXT,
    resource_id INTEGER,
    details JSON,
    ip_address TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Settings table
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value JSON NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 2.4 File System Structure

```
/workspace/
├── project_a/
│   ├── chat/
│   │   ├── session.json
│   │   ├── history.jsonl
│   │   └── summary.md
│   ├── docs/
│   ├── src/
│   ├── artifacts/
│   ├── pipeline/
│   └── project.json
├── project_b/
│   └── ...
└── ...
```

## 3. Data Flow

### 3.1 Chat Message Flow

```
User Input (Frontend)
       │
       ▼
WebSocket/HTTP POST /api/chat
       │
       ▼
Backend validates & enriches prompt
       │
       ├── Add Project Constitution
       ├── Add Session Summary
       ├── Add Selected Files
       └── Add Previous Context
       │
       ▼
Send to AI Runtime (Claude/OpenCode)
       │
       ▼
Stream response back to frontend
       │
       ├── Save to history.jsonl
       ├── Update token count
       └── Trigger artifact extraction
       │
       ▼
Update session state
```

### 3.2 Git Operation Flow

```
User Action (Frontend)
       │
       ▼
HTTP POST /api/git/:operation
       │
       ▼
Backend validates permissions
       │
       ▼
Execute git command in project workspace
       │
       ▼
Capture output & errors
       │
       ▼
Return result to frontend
       │
       ▼
Log to audit trail
```

## 4. Security Model

### 4.1 Authentication

- JWT-based authentication
- Access token (short-lived, 15 min)
- Refresh token (long-lived, 7 days)
- Role-based access control (Admin/Developer/Viewer)

### 4.2 Authorization

| Resource          | Admin | Developer | Viewer |
|-------------------|-------|-----------|--------|
| Create Project    | ✓     | ✓         | ✗      |
| Edit Project      | ✓     | ✓         | ✗      |
| Delete Project    | ✓     | ✗         | ✗      |
| Send Chat         | ✓     | ✓         | ✗      |
| Git Commit        | ✓     | ✓         | ✗      |
| Git Push          | ✓     | ✗         | ✗      |
| View Audit Logs   | ✓     | ✗         | ✗      |

### 4.3 API Security

- Rate limiting per user/IP
- Input validation on all endpoints
- SQL injection prevention (parameterized queries)
- XSS prevention (content sanitization)
- CORS configuration

## 5. Performance Considerations

### 5.1 Caching Strategy

- Session state cached in memory
- File tree cached with invalidation on changes
- Chat history paginated (50 messages per page)
- Token usage calculated incrementally

### 5.2 Streaming

- AI responses streamed via Server-Sent Events (SSE) or WebSocket
- File uploads chunked for large files
- Real-time log streaming for pipelines

### 5.3 Database Optimization

- Indexed columns: project_id, session_id, created_at
- Connection pooling
- Write-ahead logging (WAL) mode for SQLite

## 6. Scalability

### Current Design (Single VPS)

- All components on single VPS
- SQLite for simplicity
- PM2 for process management

### Future Migration Path

1. **Database**: SQLite → PostgreSQL
2. **Cache**: Memory → Redis
3. **File Storage**: Local → S3-compatible storage
4. **Horizontal Scaling**: Load balancer + multiple backend instances
5. **AI Runtime**: Local Claude → Anthropic API

## 7. Monitoring & Observability

- Health check endpoint `/api/health`
- Metrics endpoint `/api/metrics` (Prometheus format)
- Structured logging (JSON format)
- Error tracking with stack traces
- Request/response logging for debugging

---

*Document Version: 1.0*
*Status: FROZEN*
