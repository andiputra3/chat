# AI Project Manager OS - Project Final

Sistem manajemen proyek berbasis AI dengan arsitektur 3 Layer:
- **Layer 1**: AI Project Manager OS (Management & Governance)
- **Layer 2**: AI Specification Factory (Pembuat Spesifikasi)
- **Layer 3**: AI Source Generator (Pembuat Source Code)

## Struktur Direktori

```
project_final/
├── backend/           # Flask REST API
│   ├── app/
│   │   ├── models.py       # Database models
│   │   └── routes/         # API endpoints
│   ├── config.py      # Konfigurasi aplikasi
│   ├── requirements.txt
│   └── app.py         # Main application
├── frontend/          # Dashboard UI
│   └── index.html     # Single page application
├── workspace/         # Workspace untuk proyek
└── docs/             # Dokumentasi
```

## Cara Menjalankan

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Backend akan berjalan di `http://localhost:5000`

### 2. Frontend

Buka file `frontend/index.html` di browser atau serve dengan Python:

```bash
cd frontend
python -m http.server 8080
```

Frontend akan berjalan di `http://localhost:8080`

## API Endpoints

### Projects
- `GET /api/projects` - Get all projects
- `POST /api/projects` - Create new project
- `GET /api/projects/<id>` - Get project by ID
- `PUT /api/projects/<id>` - Update project
- `DELETE /api/projects/<id>` - Delete project

### Chats
- `GET /api/chats?project_id=<id>` - Get chats for project
- `POST /api/chats` - Create new chat
- `GET /api/chats/<id>` - Get chat with messages
- `POST /api/chats/<id>/messages` - Add message

### Memory (Workspace Memory)
- `GET /api/memory?project_id=<id>` - Get memory items
- `POST /api/memory` - Create memory item
- `PUT /api/memory/<id>` - Update memory
- `DELETE /api/memory/<id>` - Delete memory

### Factory (Layer 2)
- `GET /api/factory/queue` - Get factory queue
- `POST /api/factory/job` - Create factory job
- `PUT /api/factory/job/<id>` - Update job status
- `GET /api/factory/project/<id>/status` - Get project factory status

### Builder (Layer 3)
- `GET /api/builder/projects` - Get buildable projects
- `POST /api/builder/build` - Create build job
- `PUT /api/builder/build/<id>` - Update build status
- `GET /api/builder/project/<id>/history` - Get build history

### Timeline
- `GET /api/timeline/project/<id>` - Get timeline events
- `POST /api/timeline` - Create timeline event

### Notifications
- `GET /api/notifications` - Get notifications
- `POST /api/notifications` - Create notification
- `PUT /api/notifications/<id>/read` - Mark as read
- `PUT /api/notifications/read-all` - Mark all as read

## Fitur Utama

1. **Project Management** - CRUD operasi untuk proyek
2. **Chat System** - Chat sessions dengan AI Workspace Memory
3. **Factory Queue** - Antrian pekerjaan Layer 2 dengan timestamp WIB
4. **Builder** - Build management untuk Layer 3
5. **Timeline** - Timeline events untuk tracking aktivitas
6. **Notifications** - Sistem notifikasi terpusat

## Teknologi

- **Backend**: Python Flask, SQLAlchemy (SQLite)
- **Frontend**: HTML, CSS, Vanilla JavaScript
- **Database**: SQLite (default), dapat diganti PostgreSQL/MySQL
- **AI Runtime**: Siap diintegrasikan dengan OpenCode/Claude CLI

## Status

✅ Backend API berjalan dan berfungsi
✅ Database models siap
✅ Frontend dashboard dasar siap
⏳ Integrasi AI runtime (OpenCode/Claude) - perlu implementasi tambahan
⏳ Telegram notifications - perlu konfigurasi token
