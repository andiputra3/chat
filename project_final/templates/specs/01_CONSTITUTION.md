# Project Constitution: {{ project_name }}

## Purpose

This document establishes the permanent rules and guidelines that govern the {{ project_name }} project. All AI builders and human developers MUST follow these rules without exception.

## Scope

This constitution applies to:
- All source code generation
- All documentation creation
- All testing activities
- All deployment processes

## Core Principles

1. **Specification is King**: The FINAL_SPEC.md is the single source of truth. No deviations allowed.
2. **No Direct Build**: AI must never build without a frozen specification.
3. **Sandbox Boundary**: Each project is isolated in its own folder.
4. **Audit Everything**: All actions must be logged and traceable.
5. **Approval Workflow**: Draft → Review → Approved → Execute.

## Naming Conventions

### Python Code
- Variables: `snake_case`
- Functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`

### JavaScript Code
- Variables: `camelCase`
- Functions: `camelCase`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`

### Files
- Python: `snake_case.py`
- JavaScript: `camelCase.js`
- TypeScript: `PascalCase.ts`
- Documentation: `UPPER_CASE.md`

## Folder Conventions

```
{{ project_name }}/
├── docs/           # ALL .md specification files
├── src/            # Source code only
├── tests/          # Test files only
├── references/     # Input references
└── artifacts/      # Build outputs
```

## Coding Standards

### Python (PEP 8)
- Maximum line length: 100 characters
- Use type hints for all functions
- Docstrings required for all public functions
- Follow SOLID principles

### JavaScript (ESLint Standard)
- Use ES6+ features
- Prefer const over let
- Arrow functions for callbacks
- Async/await for asynchronous code

## Documentation Requirements

1. Every file must have a header comment
2. Every function must have docstring/JSDoc
3. Complex logic must have inline comments
4. API endpoints must have OpenAPI/Swagger docs

## Forbidden Rules

**FORBIDDEN**: Writing source code outside `/src/` folder
**FORBIDDEN**: Modifying `.md` files in `/docs/` after freeze
**FORBIDDEN**: Direct terminal commands for Git operations
**FORBIDDEN**: Building without approved FINAL_SPEC.md
**FORBIDDEN**: Hardcoding credentials or secrets

## Version Control

- Branch naming: `feature/{name}`, `bugfix/{name}`, `hotfix/{name}`
- Commit message format: `{type}: {description}`
- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- One commit per logical change

## Release Policy

1. All tests must pass before release
2. Build report must show score ≥ 70/100
3. Specification must be frozen
4. Approval from project owner required

## Change Management

Any changes to this constitution require:
1. Proposal document
2. Review by project owner
3. Approval vote
4. Version bump
5. Update all related documents

## Enforcement

Violations of this constitution will result in:
1. Immediate build stop
2. Error report generation
3. Manual review required
4. Correction before continuation

---

**Constitution Version**: 1.0  
**Effective Date**: 2026-07-11  
**Last Reviewed**: 2026-07-11
