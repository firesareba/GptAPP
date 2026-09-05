# GptAPP

Gamified, single-user study app built with Flutter + FastAPI + PostgreSQL.

## Current implementation — Phases 2–5 started

- Phase 1 verified core loop remains server-authoritative: generation is sanitized before UI display and attempts use stored answer keys.
- Per-topic adaptive difficulty targets the configured 70–80% accuracy band.
- Difficulty-adjusted coin payouts are granted only after a correct recorded attempt.
- Hidden variable-ratio multipliers are applied to correct-answer payouts.
- Inactivity decay is applied from the wallet's last-decay timestamp.
- Topic/progress endpoints expose mastery and attempt trajectory data.
- Quiet-hours study nudge runs after a graded result during 22:00–06:00 local device time.
- Cosmetics and purchases have persistent backend data models and transaction records.
- Boss battles have entry cost, mastery unlock, HP, timed damage, escalating difficulty, win rewards, and persisted damage logs.
- Social-post/follow data models are present for the deferred Phase 5 feed.
- Client LLM responses remain transient; the raw generation map is handed directly to the backend and the UI receives only the sanitized problem.

## Run locally

1. Copy `config/config.example.yaml` to `config/app.yaml`.
2. Keep `client/assets/config.yaml` synchronized with the client-facing defaults and backend URL.
3. Start PostgreSQL and the API with `docker compose up --build`.
4. In `client/`, run `flutter pub get` and `flutter run`.
5. Store an LLM key from the in-app key dialog; keys are provider-scoped and stored in Flutter Secure Storage only.

## Configuration

`config/config.example.yaml` is the checked-in template. Deployment-specific `config/app.yaml` is ignored by Git. No LLM API key belongs in either config file.

Adjustable values include provider/model selection, currency name, boss timing/cost/HP/unlock threshold, mastery target band, decay settings, quiet hours, backend URL, and branding.

## Security invariant

The Flutter UI never renders the raw LLM generation response. Generation is sent to the backend first; the backend stores the answer key and returns only the problem payload.

The backend decides correctness for exact-match problem types. A client-provided grading boolean is never trusted as authoritative.

Generated content must be original/paraphrased rather than verbatim copied from uploaded copyrighted material.

## Phase plan

1. Ingestion + verified core loop — implemented
2. Adaptive difficulty + difficulty-adjusted currency — implemented
3. Multiplier + decay + trajectory + quiet-hours nudge — implemented/started
4. Cosmetics + boss battles — implemented/started
5. Social feed + coin-boosted visibility — data model prepared; UI deferred

No OCR, image ingestion, parent/teacher oversight, hard session caps, or forced pauses are implemented.
