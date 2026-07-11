# AI Project Manager OS - Backend

Flask REST API untuk mengelola proyek, factory, dan builder.

## Struktur

- `app/` - Aplikasi utama
  - `api/` - Endpoint API
  - `routes/` - Route definitions
  - `models/` - Data models
  - `services/` - Business logic
  - `core/` - Core utilities
  - `utils/` - Helper functions
- `tests/` - Unit tests
- `config.py` - Konfigurasi aplikasi

## Fitur

1. **Project Management** - CRUD proyek
2. **Layer 1** - Chat, Workspace Memory, Git, Timeline, Reports
3. **Layer 2** - Project Factory (Specification Generator)
4. **Layer 3** - Project Builder (Source Code Generator)
5. **AI Runtime** - Integrasi dengan OpenCode/Claude CLI
6. **Notification** - Telegram notifications

## Menjalankan

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Server akan berjalan di `http://localhost:5000`
