# Project Identity: {{ project_name }}

## Basic Information

- **Project Name**: {{ project_name }}
- **Version**: {{ version | default('1.0.0') }}
- **Technology Stack**: {{ stack }}
- **Created**: {{ created_at | default('2026-07-11') }}
- **Last Updated**: {{ updated_at | default('2026-07-11') }}

## Project Description

{{ description | default('AI-generated project based on specification.') }}

## Project Structure

```
{{ project_name }}/
├── docs/           # Specification documents
├── src/            # Source code
├── tests/          # Test files
├── references/     # Reference materials
└── artifacts/      # Build artifacts
```

## Key Stakeholders

- **Product Owner**: {{ product_owner | default('TBD') }}
- **Lead Developer**: {{ lead_developer | default('TBD') }}
- **AI Builder**: {{ ai_builder | default('OpenCode/Claude') }}

## Status

- **Current Phase**: {{ phase | default('SPECIFICATION') }}
- **Build Status**: {{ build_status | default('NOT_STARTED') }}
- **Test Status**: {{ test_status | default('NOT_STARTED') }}
