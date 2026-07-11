# AI Project Manager OS

**Version**: 2.0.0 (Python + Flask)  
**Status**: Development  

## Overview

AI Project Manager OS is a comprehensive platform for managing software development projects with AI assistance. It features a 3-layer architecture:

- **Layer 1**: Project Manager OS (Dashboard, Chat, Memory, Git, Notifications)
- **Layer 2**: Project Factory (Specification Document Generation)
- **Layer 3**: Project Builder (Source Code Generation)

## Technology Stack

### Backend
- Python 3.10+
- Flask 3.0+
- SQLAlchemy
- SQLite (dev) / PostgreSQL (prod)

### Frontend
- HTML5, CSS3, JavaScript (ES6+)
- Custom CSS with modern design system

### AI Integration
- OpenCode CLI
- Claude Code CLI

### Git Integration
- GitPython library

## Quick Start

### Installation

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Initialize database
python app.py

# Start server
# Server runs on http://localhost:5000
```

### Frontend

Open `frontend/index.html` in a browser or serve it with a web server.

## Project Structure

```
project_final/
├── backend/
│   ├── app/
│   │   ├── models.py
│   │   ├── routes/
│   │   └── services/
│   ├── config.py
│   ├── app.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── css/styles.css
│   └── js/app.js
├── docs/           # Specification documents
├── workspace/      # Project sandboxes
├── source/         # Generated source code
└── tests/          # Test files
```

## API Endpoints

### Projects
- `GET /api/projects` - List all projects
- `POST /api/projects` - Create project
- `GET /api/projects/<id>` - Get project details
- `PUT /api/projects/<id>` - Update project
- `DELETE /api/projects/<id>` - Delete project

### Chats
- `GET /api/chats?project_id=<id>` - List chats
- `POST /api/chats` - Create chat
- `POST /api/chats/<id>/messages` - Send message

### Factory (Layer 2)
- `POST /api/factory/start` - Start specification generation
- `GET /api/factory/jobs` - List factory jobs
- `GET /api/factory/documents/<project_id>` - Get generated documents

### Builder (Layer 3)
- `POST /api/builder/start` - Start build
- `GET /api/builder/jobs/<id>` - Get build status

### Timeline
- `GET /api/timeline?project_id=<id>` - Get project timeline

### Notifications
- `GET /api/notifications` - Get notifications
- `PUT /api/notifications/<id>/read` - Mark as read

## Configuration

Set environment variables in `.env` file:

```bash
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///project_manager.db
AI_PROVIDER=opencode
AI_MODEL=deepseek-v4-flash-free
TELEGRAM_BOT_TOKEN=your-token
TELEGRAM_CHAT_ID=your-chat-id
```

## License

MIT License
