# GptAPP

Gamified, single-user study app built with Flutter + FastAPI + PostgreSQL.

## Architecture

- Flutter client for iOS, Android, Windows, macOS and Linux.
- BYOK LLM calls happen on-device; API keys are stored only in platform secure storage.
- FastAPI backend owns authoritative study state and PostgreSQL persistence.
- Phase 1 implements text/PDF ingestion, topic extraction, verified problem generation, answer submission and immutable attempts. Gamification is layered on afterward.

## Configuration

Copy `config/config.example.yaml` to `config/app.yaml` for local development. `app.yaml` is gitignored. No LLM API key belongs in config; keys are entered in the app and kept in secure storage.

Client configuration is loaded once at startup. The backend loads its configuration once at startup.

## Phase plan

1. Ingestion + verified core loop
2. Per-topic adaptive difficulty + difficulty-adjusted currency
3. Multipliers, decay, trajectory dashboard, quiet-hours nudge, session logging
4. Cosmetics + boss battles
5. Social feed and coin-boosted visibility

## Security invariant

The Flutter UI never renders the raw LLM generation response. The response is submitted to the backend first; the backend stores the answer key and returns only the problem payload.

No OCR or image ingestion is implemented or planned.
