# GptAPP

Gamified, single-user study app built with Flutter + FastAPI + PostgreSQL.

## Current implementation — Phase 1

- Flutter client scaffold with Material 3 navigation.
- Startup-loaded client configuration.
- BYOK API-key storage through Flutter Secure Storage; the key is not sent to the backend.
- FastAPI API with PostgreSQL persistence.
- Text ingestion and PDF text-layer extraction.
- PDFs without extractable text are rejected; there is no OCR path.
- Structured problem-generation intake. The raw generation response is posted to the backend before the sanitized problem is returned to the UI.
- Server-side exact-answer grading and immutable attempt records. The backend, not the client, decides whether an attempt is correct.
- Per-topic rolling mastery data model.
- Persistence models for later wallet, decay, cosmetics, boss battles and social features.

## Run locally

1. Copy `config/config.example.yaml` to `config/app.yaml`.
2. Start PostgreSQL and the API with `docker compose up --build`.
3. In `client/`, run `flutter pub get` and `flutter run`.
4. `client/assets/config.yaml` contains the client runtime defaults; update it for the API deployment you are using.

Flutter supports package dependencies through `pubspec.yaml` and installs them with `flutter pub get`. See the official Flutter package documentation for the standard workflow. urlFlutter package documentationhttps://docs.flutter.dev/packages-and-plugins/using-packages

## Configuration

`config/config.example.yaml` is the checked-in template. Deployment-specific backend configuration is kept in `config/app.yaml` and ignored by Git. No LLM API key belongs in either config file.

The client and server each load configuration once at startup; widgets and route handlers do not contain the listed adjustable values as constants.

## Security invariant

The Flutter UI never renders the raw LLM generation response. Generation is sent to the backend first; the backend stores the answer key and returns only the problem payload.

Phase 1 intentionally uses deterministic server-side answer verification. A client-side LLM grading boolean cannot be treated as authoritative because a modified client could forge it. Semantic LLM grading can be added later only with a server-verifiable trust mechanism.

Generated content must be original/paraphrased rather than verbatim copied from uploaded copyrighted material.

## Phase plan

1. Ingestion + verified core loop — implemented
2. Per-topic adaptive difficulty + difficulty-adjusted currency
3. Variable-ratio multiplier + decay + trajectory dashboard + quiet-hours nudge + session logging
4. Cosmetics + boss battles
5. Social feed + coin-boosted visibility

No OCR, image ingestion, parent/teacher oversight, hard session caps, or forced pauses are implemented.
