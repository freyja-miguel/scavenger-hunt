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

uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
npx expo start
```

## Documentation

- [Backend architecture & requirements](BACKEND_ARCHITECTURE.md)

## Features

- **Activities:** AI-generated, filterable by age, category (city/beach/bush/garden), Sydney location
- **Photo validation:** AI checks completion photos
- **Rewards:** Tokens per completed task

## Tech stack

| Layer     | Choice                 |
|----------|------------------------|
| Backend  | Python, FastAPI        |
| Frontend | React Native, Expo     |
| AI       | Groq (text + vision)   |
| Database | TBC (PostgreSQL/Supabase recommended) |
