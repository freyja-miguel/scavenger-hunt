# Treasure Hunt – Kids Activity App

A mobile treasure hunt app for kids (ages 5–12) with AI-generated activities, photo validation, and token rewards. Sydney-based for MVP.

## Team structure

- **Backend (3):** Python API, DB, AI integration
- **Frontend (3):** React Native / Expo

## Quick start

### Backend

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env with GROQ_API_KEY

python -m uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

**API base:** `http://localhost:8000/api/v1`

### Frontend

```bash
cd frontend
npm install
npx expo start
```

## Documentation

- [Backend architecture & requirements](BACKEND_ARCHITECTURE.md)

## Features

- **Registration:** Kids (5–12) register with name, date of birth, password (parent details planned for next MVP)
- **Activities:** AI-generated "find an object" tasks by age and category (beach, bush, garden, city) – e.g. find a shell, a leaf with a specific shape, or an object of a given colour and shape
- **Photo validation:** Kid photographs the found object; AI validates it matches (shape, colour, type) and awards a token on success

## Tech stack

| Layer     | Choice                 |
|----------|------------------------|
| Backend  | Python, FastAPI        |
| Frontend | React Native, Expo     |
| AI       | Groq (text + vision)   |
| Database | SQLite |

## API overview

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/api/v1/activities/` | List activities (query: `category`, `age_min`, `age_max`, `location`) |
| `POST` | `/api/v1/activities/generate` | Generate activities via AI and persist to DB |
| `POST` | `/api/v1/activities/{id}/submit-photo?child_id=1` | Submit photo for validation; awards tokens on success |
| `POST` | `/api/v1/children/register` | Register child (`name`, `date_of_birth`; optional `password`; age 5–12) |
| `GET` | `/api/v1/children/{id}` | Get child profile and token balance |
| `GET` | `/api/v1/children/{id}/tokens` | Get token balance |
| `GET` | `/api/v1/children/{id}/completions` | List completed activities |
