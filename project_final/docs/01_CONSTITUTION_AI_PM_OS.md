# Constitution: AI Project Manager OS

## Purpose

This document establishes the permanent rules and guidelines for the AI Project Manager OS project.

## Core Principles

1. **Specification is King**: FINAL_SPEC.md is the single source of truth
2. **No Direct Build**: AI never builds without frozen specification
3. **Sandbox Boundary**: Each project isolated in own folder
4. **Audit Everything**: All actions logged and traceable
5. **Approval Workflow**: Draft → Review → Approved → Execute

## Technology Stack (Official)

- **Backend**: Python 3.10+ with Flask 3.0+
- **Frontend**: HTML5 + CSS3 + JavaScript ES6+
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Realtime**: Flask-SocketIO
- **Authentication**: PyJWT
- **Git Integration**: GitPython library
- **AI Providers**: OpenCode, Claude Code via AIGateway service

## Folder Structure

```
project_final/
├── docs/           # Specification documents
├── source/         # Generated source code
├── workspace/      # Project workspaces
├── tests/          # Test files (unit, integration, e2e)
├── references/     # Input references
├── templates/      # Jinja2 templates for specs
├── assets/         # Static assets
├── config/         # Configuration files
├── scripts/        # Build/deploy scripts
├── runtime/        # Runtime configurations
└── backend/
    └── app/
        ├── services/
        │   ├── ai/         # AI Gateway service
        │   ├── auth/       # Authentication service
        │   ├── factory/    # Document generator
        │   ├── git/        # Git service
        │   ├── knowledge/  # Knowledge library
        │   └── validation/ # Validation & testing
        └── routes/         # API endpoints
```

## Forbidden Rules

**FORBIDDEN**: Writing source code outside `/source/` or `/src/` folders
**FORBIDDEN**: Modifying `.md` files in `/docs/` after freeze without approval
**FORBIDDEN**: Using terminal commands for Git operations (use GitPython only)
**FORBIDDEN**: Building without approved FINAL_SPEC.md
**FORBIDDEN**: Hardcoding credentials or secrets

## Version Control

- Branch naming: `feature/{name}`, `bugfix/{name}`, `hotfix/{name}`
- Commit format: `{type}: {description}`
- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## Release Policy

1. All tests must pass (100% unit test pass rate required)
2. Build readiness score ≥ 70/100
3. Specification frozen and approved
4. Documentation complete

---

**Version**: 2.0 (Updated for Python/Flask stack)  
**Effective Date**: 2026-07-11  
**Status**: APPROVED
