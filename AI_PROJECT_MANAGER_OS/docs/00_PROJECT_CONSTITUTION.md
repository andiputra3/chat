# Project Constitution - AI Project Manager OS

## 1. Project Vision

Membangun sistem manajemen proyek AI yang terintegrasi dengan Claude Code/OpenCode yang berjalan di VPS, dengan kemampuan:
- Manajemen proyek (buat, edit, hapus, clone, archive, restore)
- Manajemen sesi chat yang persisten per proyek
- Dashboard interaktif seperti ChatGPT
- Integrasi Git tanpa terminal
- Pipeline otomatis dari planning hingga deployment
- Audit trail lengkap

## 2. Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────────┐
│                    LAYER 1: PROJECT MANAGER                 │
│  (Dashboard + Backend API + Session Management)             │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    LAYER 2: PROJECT FACTORY                 │
│  (Specification Generator + Artifact Manager)               │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    LAYER 3: PROJECT BUILDER                 │
│  (AI Code Generator + Testing + Deployment)                 │
└─────────────────────────────────────────────────────────────┘
```

## 3. Teknologi Stack

### Backend
- **Runtime**: Node.js 20+
- **Framework**: Fastify
- **Database**: SQLite (bisa migrasi ke PostgreSQL)
- **Realtime**: WebSocket
- **Process Manager**: PM2

### Frontend
- **Framework**: React 18+
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Markdown**: react-markdown + remark-gfm
- **Code Highlight**: prismjs / highlight.js

### AI Integration
- **Claude Code CLI** (di VPS)
- **OpenCode Serve** (HTTP API)
- **9Router** (routing requests)

## 4. Struktur Folder Proyek

```
AI_PROJECT_MANAGER_OS/
├── docs/                      # Dokumentasi SSOT
├── source/
│   ├── backend/               # Backend API (Node.js + Fastify)
│   └── frontend/              # Frontend Dashboard (React + Vite)
├── tests/                     # Test suite
├── scripts/                   # Build & deployment scripts
├── config/                    # Configuration files
├── assets/                    # Static assets
├── templates/                 # Project templates
├── runtime/                   # Runtime utilities
└── workspace/                 # User projects directory
    ├── project_a/
    ├── project_b/
    └── ...
```

## 5. Workspace Structure (Per Project)

```
workspace/{project_name}/
├── chat/
│   ├── session.json           # Current session state
│   ├── history.jsonl          # Chat history (line-delimited JSON)
│   └── summary.md             # Auto-generated session summary
├── docs/                      # Project documentation
├── src/                       # Source code
├── artifacts/                 # Generated artifacts
├── pipeline/                  # Pipeline configurations
├── project.json               # Project metadata
└── .git/                      # Git repository
```

## 6. Core Principles

1. **Single Source of Truth (SSOT)**: Semua spesifikasi didokumentasikan sebelum coding
2. **Session Isolation**: Setiap sesi chat terpisah dan tidak saling bercampur
3. **Context Efficiency**: Menggunakan summarization untuk mengurangi token usage
4. **Audit Trail**: Semua aktivitas tercatat dan tidak dapat diubah
5. **Zero Terminal**: Semua operasi Git/Claude dilakukan via dashboard
6. **Pipeline First**: Setiap task melalui pipeline yang terdefinisi

## 7. Security Requirements

- JWT Authentication dengan role-based access (Admin/Developer/Viewer)
- API Key untuk komunikasi dengan VPS
- Input validation pada semua endpoint
- File permission management
- Audit log immutable

## 8. Performance Targets

- Response time < 500ms untuk operasi lokal
- Streaming output untuk AI responses
- Concurrent session support (minimal 10 sesi aktif)
- Token usage tracking real-time

## 9. Compliance & Governance

- Project Constitution tidak boleh berubah saat implementasi
- Specification Freeze sebelum Phase 2 (Backend Core)
- Change management melalui version control
- Approval workflow untuk perubahan kritis

## 10. Success Criteria

1. Dashboard berfungsi seperti ChatGPT dengan integrasi Claude Code real
2. Manajemen sesi persisten antar restart aplikasi
3. Git operations tanpa terminal
4. Pipeline otomatis dari planning hingga deployment
5. Audit trail lengkap untuk semua aktivitas
6. Context management efisien (tidak brainstorming karena sesi panjang)

---

*Document Version: 1.0*
*Status: FROZEN*
*Last Updated: $(date +%Y-%m-%d)*
