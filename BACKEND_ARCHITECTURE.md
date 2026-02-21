# Treasure Hunt Backend – Architecture & Requirements

## Overview

Backend for a kids’ treasure hunt app (ages 5–12) with AI-generated activities, photo validation, and token rewards. Scope is Sydney for MVP.

---

## 1. Core Features & Backend Responsibilities

### 1.1 Activity Generation (AI)
| Requirement | Backend Implementation |
|-------------|------------------------|
| AI-generated activity list | Call Groq to create object-based scavenger hunt activities |
| Age group filtering | Simpler tasks for 5–7, more specific (shape/color/texture) for 8–12 |
| Location-based (Sydney MVP) | Sydney suburbs/areas in DB; activities tagged with location |
| Categories | `city`, `beach`, `bush`, `garden` – each suggests object types |

**Activity format:** "Find an object" tasks – e.g. find a shell on a beach, a leaf with a specific shape, an object of X shape and Y colour. Kid takes a photo of the object; AI validates and awards a token on success.

### 1.2 Photo Validation (AI)
| Requirement | Backend Implementation |
|-------------|------------------------|
| Take a photo | Kid photographs the found object; app uploads image |
| AI validation | Groq vision (Llama 4 Scout) checks object matches criteria (shape, colour, type) |
| Must be taken at the time | EXIF timestamp optional (future anti-cheat) |

**Validation flow:** Kid finds object → Takes photo → Upload → AI checks photo shows correct object (type, shape, colour) → Approve/Reject → Token awarded on success

### 1.3 Rewards System
| Requirement | Backend Implementation |
|-------------|------------------------|
| Token per completed task | Award token when photo validation succeeds |
| Store balance | Persist tokens per child/family account |

---

## 2. Technical Stack (Backend)

| Layer | Choice | Notes |
|-------|--------|------|
| **Language** | Python 3.11+ | Confirmed |
| **Framework** | FastAPI | Async, OpenAPI, validation |
| **Database** | SQLAlchemy 2 (async) + SQLite | Via aiosqlite driver |
| **AI – Text** | Groq API | LLM for activity generation |
| **AI – Vision** | Groq API (Llama 4 Scout) | Photo validation |
| **File Storage** | Local `uploads/` directory | For activity photos (MVP) |

---

## 3. Database

**SQLite** with `aiosqlite` (async driver). Database file: `treasure_hunt.db` in the backend directory. Zero setup, file-based, suitable for MVP.

**Note:** If you had an existing database before the kid registration update, delete `treasure_hunt.db` and restart the app to recreate tables with the new schema.

---

## 4. Data Model (Implemented)

ORM: `app/db/models.py` (SQLAlchemy).

```
Child
├── id (PK)
├── name
├── date_of_birth
├── password_hash (bcrypt)
├── parent_account_id (optional; for next MVP)
├── token_balance
└── created_at
   (+ age computed from date_of_birth)

Activity
├── id (PK)
├── title
├── description (AI-generated)
├── category (city|beach|bush|garden)
├── age_min, age_max
├── location_sydney (suburb/area name)
├── ai_validation_prompt (what to check in photo)
├── tokens_reward
└── created_at

ActivityCompletion
├── id (PK)
├── child_id (FK)
├── activity_id (FK)
├── photo_path (local path; S3/R2 key when added)
├── photo_timestamp (optional, from EXIF)
├── validated (bool)
├── validation_response (AI reasoning)
├── tokens_awarded
└── completed_at
```

---

## 5. API Endpoints (Implemented)

All under prefix `/api/v1`.

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/activities/` | List activities (query: `category`, `age_min`, `age_max`, `location`) |
| `POST` | `/activities/generate` | Generate activities via AI and persist to DB |
| `POST` | `/activities/{id}/submit-photo?child_id={id}` | Submit photo (multipart); validate via AI; award tokens on success |
| `POST` | `/children/register` | Register child (body: `name`, `date_of_birth`; optional `password` min 6 chars; age 5–12) |
| `GET` | `/children/{id}` | Get child profile and token balance |
| `GET` | `/children/{id}/tokens` | Get child token balance |
| `GET` | `/children/{id}/completions` | List completed activities (with activity title, tokens_awarded, validated) |

---

## 6. AI Integration

### 6.1 Activity Generation (Groq)
- **Model:** `llama-3.1-70b-versatile`
- **Input:** age band, category (beach/bush/garden/city), Sydney location
- **Output:** Object-based tasks with title, description, `ai_validation_prompt` (shape/colour/type)
- **Examples:** "Find a spiral shell on the beach", "Find a heart-shaped leaf", "Find something round and blue"

### 6.2 Photo Validation (Groq Vision)
- **Model:** `meta-llama/llama-4-scout-17b-16e-instruct`
- **Input:** Base64/URL image + activity description + validation criteria
- **Output:** Structured JSON: `{ "valid": bool, "reasoning": str }`
- **Note:** Image size limit 4MB base64 / 20MB URL

### 6.3 Anti-cheat (Photo freshness)
- Check EXIF `DateTimeOriginal` – reject if too old
- Optional: compare photo location with activity location (within tolerance)

---

## 7. Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, lifespan (init_db)
│   ├── config.py            # Pydantic Settings (env vars)
│   ├── models/              # Pydantic request/response schemas
│   │   └── schemas.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py          # Engine, async session, init_db
│   │   └── models.py        # SQLAlchemy ORM (Child, Activity, ActivityCompletion)
│   ├── routes/
│   │   ├── activities.py
│   │   └── children.py
│   └── services/
│       ├── ai_service.py    # Groq text + vision
│       └── activity_service.py  # List, persist, submit-photo logic
├── requirements.txt
├── run.py
└── .env.example
```

---

## 8. Environment Variables

See `backend/.env.example`. Loaded via `app/config.py` (Pydantic Settings).

```env
# Database (SQLite)
DATABASE_URL=sqlite+aiosqlite:///./treasure_hunt.db

# AI (Groq) – required for generate and submit-photo
GROQ_API_KEY=your_groq_api_key

# App
DEBUG=true
API_PREFIX=/api/v1
UPLOAD_DIR=uploads
PHOTO_MAX_AGE_MINUTES=60

# Sydney bounds (optional)
SYDNEY_LAT_MIN=-34.2
SYDNEY_LAT_MAX=-33.6
SYDNEY_LON_MIN=150.5
SYDNEY_LON_MAX=151.4

# Future: Storage (S3/R2), JWT_SECRET, API_RATE_LIMIT
```

---

## 9. Frontend–Backend Contract (Notes for Frontend Team)

- **Base URL:** `{host}/api/v1`
- **Register child:** `POST /children/register` with JSON `{ "name": string, "date_of_birth": "YYYY-MM-DD", "password"?: string }` (age 5–12; password optional, min 6 chars if provided). Parent details planned for next MVP.
- **List activities:** `GET /activities/?category=beach&age_min=5&age_max=8&location=Bondi` (all query params optional).
- **Submit photo:** `POST /activities/{id}/submit-photo?child_id={child_id}` with multipart form field `photo` (image file, max 20MB). Response: `{ "valid": bool, "reasoning": string, "tokens_awarded": number }`.
- **Tokens:** Returned in `GET /children/{id}` as `token_balance`, and in submit-photo response as `tokens_awarded`.
- **Auth:** Not yet implemented; to be added (JWT or Supabase Auth).

---

## 10. MVP Milestones (Backend)

1. [x] Set up FastAPI app + basic health check
2. [x] DB schema (SQLAlchemy; tables created on startup via `init_db`)
3. [x] Groq activity generation endpoint + persist to DB
4. [x] Groq vision photo validation endpoint
5. [x] Token award on successful validation
6. [x] Image storage (local `uploads/` directory)
7. [x] Kid registration (name, date_of_birth, password)
8. [ ] Parent/guardian details (required for registration – next MVP)
9. [ ] Login / session (JWT) for authenticated requests
10. [ ] EXIF/photo freshness check (optional anti-cheat)
11. [ ] Alembic migrations (for production schema changes)

---

*Document version: 1.1 – Feb 2025*
