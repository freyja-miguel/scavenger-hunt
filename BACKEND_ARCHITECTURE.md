# Treasure Hunt Backend – Architecture & Requirements

## Overview

Backend for a kids’ treasure hunt app (ages 5–12) with AI-generated activities, photo validation, and token rewards. Scope is Sydney for MVP.

---

## 1. Core Features & Backend Responsibilities

### 1.1 Activity Generation (AI)
| Requirement | Backend Implementation |
|-------------|------------------------|
| AI-generated activity list | Call Groq/Cloudflare AI to create activities |
| Age group filtering | Store child age; filter/personalise prompts per age band |
| Location-based (Sydney MVP) | Sydney suburbs/areas in DB; activities tagged with location |
| Categories | `city`, `beach`, `bush`, `garden` – store and filter by category |

**Suggested age bands:** 5–7, 8–10, 11–12 (or per your product spec)

### 1.2 Photo Validation (AI)
| Requirement | Backend Implementation |
|-------------|------------------------|
| Take a photo | App uploads image; backend stores and processes it |
| AI validation | Groq vision models (e.g. Llama 4 Scout) to verify activity completion |
| Must be taken at the time | Use EXIF timestamp and/or geolocation for basic fraud checks |

**Validation flow:** Upload image → Extract metadata (time, location) → AI prompt to compare image with activity description → Approve/Reject

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
| **Database** | TBC – see options below | |
| **AI – Text** | Groq API | LLM for activity generation |
| **AI – Vision** | Groq API (Llama 4 Scout/Maverick) | Photo validation |
| **File Storage** | Local/S3/R2 | For activity photos |

---

## 3. Database Options (TBC)

| Option | Pros | Cons | Best For |
|--------|------|------|----------|
| **PostgreSQL** | Mature, relational, JSON support | Needs hosting | Production, multi-user |
| **Supabase** | Managed Postgres, auth, storage | Vendor lock-in | Fast MVP with auth + storage |
| **SQLite** | Zero setup, file-based | Not ideal for many concurrent users | Local dev, small MVP |
| **MongoDB** | Flexible schema | Less strict structure | Prototyping, document-style data |

**Recommendation for MVP:** PostgreSQL via Supabase (managed Postgres + auth + storage).

---

## 4. Data Model (Draft)

```
Child
├── id (PK)
├── name
├── age (for age band filtering)
├── parent_account_id (FK)
├── token_balance
└── created_at

Activity
├── id (PK)
├── title
├── description (AI-generated)
├── category (city|beach|bush|garden)
├── age_min, age_max
├── location_sydney (suburb/area name)
├── ai_prompt_for_validation (what to check in photo)
└── tokens_reward

ActivityCompletion
├── id (PK)
├── child_id (FK)
├── activity_id (FK)
├── photo_url (path or S3/R2 key)
├── photo_timestamp (from EXIF or upload time)
├── validated (bool)
├── validation_response (AI reasoning)
└── completed_at
```

---

## 5. API Endpoints (Draft)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/activities` | List activities (filters: age, category, location) |
| `POST` | `/activities/generate` | Generate new activities via AI (admin/internal) |
| `POST` | `/activities/{id}/submit-photo` | Submit photo for validation |
| `GET` | `/children/{id}/tokens` | Get child token balance |
| `GET` | `/children/{id}/completions` | List completed activities |

---

## 6. AI Integration

### 6.1 Activity Generation (Groq)
- **Model:** e.g. `llama-3.1-70b-versatile` (or current recommended model)
- **Input:** age band, category, Sydney location
- **Output:** Structured JSON with title, description, validation criteria

### 6.2 Photo Validation (Groq Vision)
- **Model:** `meta-llama/llama-4-scout-17b-16e-instruct`
- **Input:** Base64/URL image + activity description + validation criteria
- **Output:** Structured JSON: `{ "valid": bool, "reasoning": str }`
- **Note:** Image size limit 4MB base64 / 20MB URL

### 6.3 Anti-cheat (Photo freshness)
- Check EXIF `DateTimeOriginal` – reject if too old
- Optional: compare photo location with activity location (within tolerance)

---

## 7. Suggested Project Structure

```
treasure-hunt/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Env vars
│   │   ├── models/              # SQLAlchemy/Pydantic models
│   │   ├── routes/              # API routes
│   │   ├── services/
│   │   │   ├── ai_service.py    # Groq integration
│   │   │   ├── activity_service.py
│   │   │   └── validation_service.py
│   │   └── db/                  # DB setup, migrations
│   ├── requirements.txt
│   └── .env.example
├── frontend/                    # React Native / Expo
└── BACKEND_ARCHITECTURE.md
```

---

## 8. Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:pass@host:5432/treasure_hunt

# AI (Groq)
GROQ_API_KEY=your_groq_api_key

# Storage (when using S3/R2)
S3_BUCKET=
S3_REGION=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=

# Security
JWT_SECRET=
API_RATE_LIMIT=100  # requests per minute
```

---

## 9. Frontend–Backend Contract (Notes for Frontend Team)

- **Auth:** JWT or Supabase Auth (depending on DB choice)
- **File upload:** Multipart form data to `/activities/{id}/submit-photo`
- **AI responses:** Structured JSON; handle validation failure gracefully
- **Tokens:** Returned in child profile and on completion events

---

## 10. MVP Milestones (Backend)

1. [ ] Set up FastAPI app + basic health check
2. [ ] DB schema + migrations (child, activity, completion)
3. [ ] Groq activity generation endpoint
4. [ ] Groq vision photo validation endpoint
5. [ ] Token award on successful validation
6. [ ] Auth integration (align with frontend)
7. [ ] Image storage (local or S3/R2)

---

*Document version: 1.0 – Feb 2025*
