# AI Project Manager OS - Updated Specification

## Technology Stack (Updated)

This specification has been officially updated to reflect the **Python + Flask** implementation.

### Backend
- **Language**: Python 3.10+
- **Framework**: Flask 3.0+
- **Database**: SQLAlchemy with SQLite (dev) / PostgreSQL (prod)
- **CORS**: flask-cors
- **WebSocket**: Flask-SocketIO (for real-time AI streaming)

### Frontend
- **Core**: HTML5, CSS3, JavaScript (ES6+)
- **Styling**: Custom CSS with Tailwind-inspired utilities
- **UI Components**: Vanilla JavaScript with modular architecture
- **Real-time**: Socket.IO client for WebSocket communication

### AI Integration
- **Primary**: OpenCode CLI
- **Secondary**: Claude Code CLI
- **Gateway**: Custom AI Gateway service (9Router compatible)
- **Modes**: Plan mode (`--mode plan`), Build mode (default)

### Git Integration
- **Library**: GitPython
- **Operations**: All via API (no terminal commands)

### Authentication
- **Method**: JWT (PyJWT)
- **RBAC**: Role-based access control (Admin, Developer, Viewer)

### Deployment
- **Process Manager**: PM2 or Gunicorn
- **Reverse Proxy**: Nginx
- **Environment**: Docker-ready

---

## Architecture Overview

### Layer 1: AI Project Manager OS
Dashboard and management layer with:
- Project CRUD operations
- Chat interface with AI streaming
- Workspace memory management
- Knowledge library
- Timeline tracking
- Notification center
- Git management
- Reports and analytics

### Layer 2: Project Factory
Specification generation layer:
- Input processing (ide + references)
- Reference analysis
- 22 document generation
- Cross-validation
- FINAL_SPEC compilation
- Build passport generation
- Freeze mechanism

### Layer 3: Project Builder
Source code generation layer:
- Build planning
- AI execution
- Source generation
- Validation
- Testing
- Report generation
- Git commit

---

## Folder Structure

```
project_final/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── projects.py
│   │   │   ├── chats.py
│   │   │   ├── memory.py
│   │   │   ├── factory.py
│   │   │   ├── builder.py
│   │   │   ├── timeline.py
│   │   │   ├── notifications.py
│   │   │   ├── telegram_config.py
│   │   │   ├── auth.py              [NEW]
│   │   │   ├── git_manager.py       [NEW]
│   │   │   └── knowledge.py         [NEW]
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── telegram_service.py
│   │   │   ├── ai/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── ai_gateway.py    [NEW]
│   │   │   │   ├── opencode_service.py [NEW]
│   │   │   │   ├── claude_service.py   [NEW]
│   │   │   │   └── prompt_engine.py    [NEW]
│   │   │   ├── git/
│   │   │   │   ├── __init__.py
│   │   │   │   └── git_service.py      [NEW]
│   │   │   └── factory/
│   │   │       ├── __init__.py
│   │   │       ├── document_generator.py [NEW]
│   │   │       ├── validator.py          [NEW]
│   │   │       └── compiler.py           [NEW]
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── auth_utils.py        [NEW]
│   │       └── file_utils.py        [NEW]
│   ├── config.py
│   ├── app.py
│   ├── requirements.txt
│   └── instance/
│       └── project_manager.db
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── styles.css             [NEW]
│   ├── js/
│   │   ├── app.js                 [NEW]
│   │   ├── components/            [NEW]
│   │   │   ├── dashboard.js
│   │   │   ├── chat.js
│   │   │   ├── projects.js
│   │   │   ├── factory.js
│   │   │   └── builder.js
│   │   └── services/              [NEW]
│   │       ├── api.js
│   │       ├── socket.js
│   │       └── auth.js
│   └── components/                [NEW]
├── docs/                          [NEW - 22 spec files]
├── source/                        [NEW - generated code]
├── workspace/                     [NEW - project sandboxes]
├── tests/                         [NEW - test files]
├── runtime/                       [NEW - runtime config]
├── config/                        [NEW - configurations]
├── scripts/                       [NEW - build/deploy scripts]
├── assets/                        [NEW - static assets]
├── templates/                     [NEW - document templates]
└── references/                    [NEW - uploaded references]
```

---

## 22 Specification Documents

Layer 2 generates these documents in `/docs/`:

1. `00_PROJECT_IDENTITY_{PROJECT}.md`
2. `01_CONSTITUTION_{PROJECT}.md`
3. `02_REQUIREMENTS_{PROJECT}.md`
4. `03_VARIABLES_{PROJECT}.md`
5. `04_FUNCTIONS_{PROJECT}.md`
6. `05_PIPELINE_{PROJECT}.md`
7. `06_DATA_CONTRACTS_{PROJECT}.md`
8. `07_STATE_MACHINES_{PROJECT}.md`
9. `08_DEPENDENCY_MATRIX_{PROJECT}.md`
10. `09_BUSINESS_RULES_{PROJECT}.md`
11. `10_TEST_CASES_{PROJECT}.md`
12. `11_FORBIDDEN_RULES_{PROJECT}.md`
13. `12_ID_TRACKING_{PROJECT}.md`
14. `13_OBJECT_DICTIONARY_{PROJECT}.md`
15. `14_EVENT_DICTIONARY_{PROJECT}.md`
16. `15_STATE_DICTIONARY_{PROJECT}.md`
17. `16_PATTERN_DICTIONARY_{PROJECT}.md`
18. `17_FEATURE_REGISTRY_{PROJECT}.md`
19. `18_INTERACTION_MATRIX_{PROJECT}.md`
20. `19_AI_BUILD_GUARD_{PROJECT}.md`
21. `20_OPERATIONAL_ORIENTATION_{PROJECT}.md`
22. `FINAL_SPEC_{PROJECT}.md`

Plus: `build_passport.json`

---

## Governance Rules

### Specification is King
- All implementations must follow FINAL_SPEC.md
- No design decisions during build phase
- Changes require approval workflow

### Sandbox Boundary
- Each project isolated in `workspace/{project_name}/`
- No cross-project contamination
- AI restricted to project folder

### No Direct Build
- AI cannot build without frozen specification
- Build passport required before Layer 3 execution

### Audit Everything
- All actions logged to timeline
- Immutable audit trail
- Decision tracking mandatory

---

## API Endpoints

### Authentication
- `POST /api/auth/login`
- `POST /api/auth/register`
- `POST /api/auth/refresh`
- `POST /api/auth/logout`

### Projects
- `GET /api/projects`
- `POST /api/projects`
- `GET /api/projects/<id>`
- `PUT /api/projects/<id>`
- `DELETE /api/projects/<id>`
- `POST /api/projects/<id>/clone`
- `POST /api/projects/<id>/archive`

### Chats
- `GET /api/chats?project_id=<id>`
- `POST /api/chats`
- `GET /api/chats/<id>`
- `DELETE /api/chats/<id>`
- `POST /api/chats/<id>/messages`
- `GET /api/chats/<id>/messages`

### Memory
- `GET /api/memory?project_id=<id>`
- `POST /api/memory`
- `PUT /api/memory/<id>`
- `DELETE /api/memory/<id>`
- `POST /api/memory/<id>/snapshot`

### Factory
- `POST /api/factory/start`
- `GET /api/factory/jobs`
- `GET /api/factory/jobs/<id>`
- `POST /api/factory/jobs/<id>/review`
- `POST /api/factory/jobs/<id>/approve`
- `GET /api/factory/documents/<project_id>`

### Builder
- `GET /api/builder/projects`
- `POST /api/builder/start`
- `GET /api/builder/jobs/<id>`
- `GET /api/builder/reports/<id>`

### Timeline
- `GET /api/timeline?project_id=<id>`
- `POST /api/timeline`

### Notifications
- `GET /api/notifications`
- `PUT /api/notifications/<id>/read`
- `PUT /api/notifications/read-all`

### Git
- `POST /api/git/init`
- `POST /api/git/commit`
- `POST /api/git/branch`
- `POST /api/git/push`
- `POST /api/git/pull`
- `GET /api/git/status`
- `GET /api/git/log`

### Knowledge
- `GET /api/knowledge`
- `POST /api/knowledge`
- `GET /api/knowledge/<id>`
- `PUT /api/knowledge/<id>`
- `DELETE /api/knowledge/<id>`

---

## Build Readiness Checklist

### Critical (Must Have)
- [x] Flask backend structure
- [ ] AI Gateway integration
- [ ] Layer 2 document generation
- [ ] Layer 3 build execution
- [ ] Authentication (JWT)
- [ ] Git integration
- [ ] WebSocket for streaming

### High Priority
- [ ] Complete dashboard UI
- [ ] Reference upload/analysis
- [ ] Cross-validation logic
- [ ] Test framework
- [ ] Session management enhancements

### Medium Priority
- [ ] Knowledge library
- [ ] Benchmark module
- [ ] Reports module
- [ ] Token/cost tracking

### Low Priority
- [ ] Clone/archive/restore
- [ ] Advanced settings
- [ ] UI polish

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-07-11 | Initial specification (Node.js + React) |
| 2.0.0 | 2026-07-11 | **Updated to Python + Flask** |

---

*This specification is the Single Source of Truth (SSOT) for the AI Project Manager OS project.*
