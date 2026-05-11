# 🤖 AI Interviewer

> **Autonomous, FAANG-grade mock interview platform powered by a multi-agent AI pipeline with real-time multimodal analysis.**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-ai--interviewer--7w1u.onrender.com-2563EB?style=for-the-badge)](https://ai-interviewer-7w1u.onrender.com/login)

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
- [Environment Variables](#-environment-variables)
- [One-Command Run](#-one-command-run)
- [Production Build & Deployment](#-production-build--deployment)
- [API Reference](#-api-reference)
- [Sample Inputs & Outputs](#-sample-inputs--outputs)
- [Tech Stack](#-tech-stack)
- [Contributing](#-contributing)

---

## 🎯 Overview

AI Interviewer is a full-stack web application that conducts intelligent, adaptive mock interviews. Candidates upload their resume, select a target role and company persona (Google, Meta, Amazon, etc.), and are interviewed by **Aura** — an AI interviewer that:

- Asks **context-aware questions** grounded in the candidate's own resume and skills
- **Adapts difficulty in real time** based on answer quality
- **Analyses audio** (confidence, speech rate, filler words) using librosa signal processing
- **Analyses video** (eye contact, posture, stress) using MediaPipe face and pose landmarks
- Delivers a **detailed coaching report** with strengths, gaps, and improvement tips

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎙️ Voice Interview | AI asks questions via TTS; candidate responds via speech-to-text |
| 📄 Resume Intelligence | Parses PDF/DOCX/TXT resumes into structured skills, experience, and projects |
| 🧠 6 Specialised Agents | Context, Orchestrator, Memory, Visual, Technical, Feedback agents |
| 📊 Real-time Scoring | Technical, Communication, Confidence, Engagement, Depth, Stress metrics |
| 🎯 Adaptive Difficulty | Automatically adjusts question difficulty based on rolling performance |
| 💻 Coding Round | Embedded code editor with hidden test-case execution (Python, JS, C++) |
| 🔒 Google OAuth | Sign in with Google or email/password |
| 📈 Analytics Dashboard | Radar chart, score breakdowns, and per-question feedback |
| 🏢 Company Personas | Practice for Google, Meta, Amazon, Microsoft, and more |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                 BROWSER  (React + Vite + TypeScript)            │
│  Pages: Login │ Resume │ Coaching │ InterviewSuite │ Analytics  │
│  Hooks: useAudioIntel │ useVisualIntel │ useSpeech │ useOAuth   │
│  State: Zustand (authStore, interviewStore)                     │
└──────────────────────────────┬──────────────────────────────────┘
                               │  HTTPS REST  /api/*
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│              FASTAPI BACKEND  (Python 3.11 + Uvicorn)           │
│  Routes: /auth  /resume  /interview  /jobs                      │
│  Auth: JWT bearer tokens │ CORS │ Pydantic validation           │
└──┬──────────┬──────────┬──────────┬──────────┬─────────────────┘
   │          │          │          │          │
Agent1    Agent2    Agent3    Agent4    Agent5    Agent6
Context  Orchestr- Interview  Visual   Technical  Feedback
Module    ator     Memory     Intel    Evaluator   Agent
   │          │          │          │          │
   └──────────┴──────────┴──────────┴──────────┘
                     │  Groq API  (llama-3.1-8b-instant)
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│        DATABASE  (SQLite local │ PostgreSQL production)         │
│  Tables: users │ resumes │ interview_sessions │ interview_qa    │
└─────────────────────────────────────────────────────────────────┘
```

### Agent Responsibilities

| Agent | Name | Role |
|---|---|---|
| Agent 1 | Context Module | Parses resume → extracts skills, experience, projects, gaps, market roles |
| Agent 2 | Orchestrator | Session state machine, question generation, adaptive difficulty engine |
| Agent 3 | Interview Memory | Deduplication, topic coverage tracking, weakness history |
| Agent 4 | Visual Intelligence | MediaPipe face/pose landmarks → eye contact, posture, stress, engagement |
| Agent 5 | Technical Evaluator | Groq semantic scoring of answers + keyword heuristic fallback |
| Agent 6 | Feedback Agent | Post-interview coaching report via Groq + rule-based fallback |

---

## 📁 Project Structure

```
Ai-Interviewer/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── orchestrator.py          # Session management & question generation
│   │   │   ├── context_module.py        # Resume parsing & context analysis
│   │   │   ├── interview_memory.py      # Conversation memory & tracking
│   │   │   ├── visual_intelligence.py   # MediaPipe video analysis
│   │   │   ├── technical_evaluator.py   # Answer scoring
│   │   │   ├── feedback_agent.py        # Post-interview coaching
│   │   │   ├── audio_intelligence.py    # librosa audio analysis
│   │   │   ├── coding_evaluator.py      # Coding challenge evaluation
│   │   │   └── code_executor.py         # Sandboxed code runner
│   │   ├── routes/
│   │   │   ├── auth.py                  # /api/auth/*
│   │   │   ├── resume.py                # /api/resume/*
│   │   │   ├── interview.py             # /api/interview/*
│   │   │   └── jobs.py                  # /api/jobs/*
│   │   ├── services/
│   │   │   ├── groq_client.py           # Shared Groq async client
│   │   │   ├── job_recommender.py       # Resume ↔ job matching
│   │   │   └── resume_parser.py         # PDF/DOCX/TXT extraction
│   │   ├── models/
│   │   │   ├── db_models.py             # SQLAlchemy ORM models
│   │   │   └── schemas.py               # Pydantic schemas
│   │   ├── main.py                      # App factory & lifespan
│   │   ├── database.py                  # Async DB engine
│   │   └── auth_deps.py                 # JWT dependency injection
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   └── src/
│       ├── pages/                       # Route-level components
│       ├── components/                  # Reusable UI components
│       ├── hooks/                       # useAudioIntel, useVisualIntel, useSpeech
│       ├── store/                       # Zustand state stores
│       └── lib/api.ts                   # Typed Axios wrapper
│
└── start_servers.sh                     # One-command local run
```

---

## 🛠️ Prerequisites

| Dependency | Version | Purpose |
|---|---|---|
| Python | 3.11+ | Backend runtime |
| Node.js | 18+ | Frontend build toolchain |
| npm | 9+ | Package manager |
| Groq API Key | — | LLM inference ([get one free](https://console.groq.com)) |
| Git | Any | Clone the repo |

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/srikar-1810/Ai-Interviewer.git
cd Ai-Interviewer

```bash
cd backend

# Create and activate virtual environment
python3.11 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Open .env and fill in your GROQ_API_KEY (see Environment Variables below)

# Start the backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Backend will be live at **http://localhost:8000**

### 3. Set up the frontend

```bash
# In a new terminal
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

Frontend will be live at **http://localhost:5173**

---

## 🔑 Environment Variables

Create `backend/.env` with the following:

```env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
SECRET_KEY=your-long-random-secret-key
DATABASE_URL=sqlite+aiosqlite:///./interview.db
GROQ_MODEL=llama-3.1-8b-instant
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
BACKEND_URL=http://127.0.0.1:8000
FRONTEND_URL=http://localhost:5173
```

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | ✅ Yes | Your Groq Cloud API key. Used server-side only for all LLM calls. Get it at [console.groq.com](https://console.groq.com) |
| `SECRET_KEY` | ✅ Yes | Secret string used as the seed for JWT token signing. Use a long random value. Generate with: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `DATABASE_URL` | ✅ Yes | SQLAlchemy async connection string. Use `sqlite+aiosqlite:///./interview.db` locally. For production: `postgresql+asyncpg://user:pass@host:5432/dbname` |
| `GROQ_MODEL` | Optional | Groq model identifier. Defaults to `llama-3.1-8b-instant`. Switch to `llama-3.1-70b-versatile` for higher quality (higher latency). |
| `GOOGLE_CLIENT_ID` | Optional | Required only if enabling Google OAuth sign-in |
| `GOOGLE_CLIENT_SECRET` | Optional | Required only if enabling Google OAuth sign-in |
| `FRONTEND_URL` | Optional | Frontend origin for CORS and OAuth redirects. Defaults to `http://localhost:5173` |
| `BACKEND_URL` | Optional | Backend URL for OAuth callback construction. Defaults to `http://127.0.0.1:8000` |

---

## ⚡ One-Command Run

Start both backend and frontend with a single command:

```bash
bash start_servers.sh
```

This script:
1. Kills any existing backend or frontend processes
2. Starts FastAPI backend on port **8000** (logs → `/tmp/backend.log`)
3. Starts Vite dev server on port **5173** (logs → `/tmp/frontend.log`)
4. Runs a health check on both servers
5. Prints confirmation with URLs

View logs if something fails:

```bash
tail -f /tmp/backend.log
tail -f /tmp/frontend.log
```

---

## 📦 Production Build & Deployment

### Frontend Build

```bash
cd frontend
npm run build        # Outputs optimised bundle to frontend/dist/
npm run preview      # Preview production build locally on port 4173
```

### Backend Production Run

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Deploy on Render

| Service | Type | Config |
|---|---|---|
| Backend | Web Service (Python 3.11) | Build: `pip install -r requirements.txt` · Start: `uvicorn app.main:app --host 0.0.0.0 --port 8000` |
| Frontend | Static Site | Build: `npm install && npm run build` · Publish Dir: `dist` |
| Database | PostgreSQL Add-on | Auto-injects `DATABASE_URL` as env var |

Set the following in your Render dashboard under **Environment**:

```
GROQ_API_KEY        = <your key>
SECRET_KEY          = <random string>
DATABASE_URL        = <injected by Render PostgreSQL>
FRONTEND_URL        = https://your-frontend.onrender.com
BACKEND_URL         = https://your-backend.onrender.com
```

---

## 📡 API Reference

### Authentication

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/auth/register` | No | Register with email + password. Returns JWT token. |
| `POST` | `/api/auth/login` | No | Login. Returns JWT token. |
| `GET` | `/api/auth/google` | No | Redirect to Google OAuth. |
| `GET` | `/api/auth/google/callback` | No | OAuth callback. Returns token via redirect. |

### Resume

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/resume/upload` | Yes | Upload PDF/DOCX/TXT. Returns `resume_id` + parsed data. |
| `GET` | `/api/resume/{id}` | Yes | Get parsed resume (skills, experience, projects). |
| `GET` | `/api/resume/{id}/context` | Yes | Full context analysis: skill scores, market roles, focus areas. |

### Interview

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/interview/start` | Yes | Start session. Body: `{ resume_id, persona, difficulty }` → returns `session_id` + first question. |
| `POST` | `/api/interview/{id}/answer` | Yes | Submit answer. Body: `{ answer, audio_base64, frames }` → returns metrics + next question. |
| `POST` | `/api/interview/{id}/end` | Yes | End session. Returns aggregated scores + feedback report. |
| `GET` | `/api/interview/{id}/status` | Yes | Get live session status and current metrics. |
| `POST` | `/api/interview/analyze-frame` | Yes | Analyse single webcam frame. Returns posture, eye contact, stress scores. |
| `POST` | `/api/interview/analyze-audio` | Yes | Analyse audio chunk. Returns confidence, clarity, speech rate. |
| `POST` | `/api/interview/coding/start` | Yes | Start coding round. Returns challenge + `session_id`. |
| `POST` | `/api/interview/coding/{id}/execute` | Yes | Execute code against test cases. Returns pass/fail results. |

### Jobs

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/jobs/recommend/{resume_id}` | No | Returns matched job listings for a resume. |
| `GET` | `/api/jobs/all` | No | Returns all available job listings. |
| `GET` | `/api/health` | No | Health check. Returns DB status and Groq key status. |

All protected endpoints require: `Authorization: Bearer <token>` header.

---

## 📋 Sample Inputs & Outputs

### Sample Resume (Input)

```
Arjun Sharma | arjun.sharma@email.com
Senior Backend Engineer, TechCorp India (2021–2024)
  - Built FastAPI microservices serving 2M daily active users
  - Designed Redis caching layer reducing DB load by 60%
  - Led Docker/Kubernetes migration on AWS EKS
Skills: Python, FastAPI, PostgreSQL, Redis, Docker, Kubernetes, AWS, React
```

### Expected Score Output

```json
{
  "technical_score": 78,
  "depth_score": 72,
  "communication_score": 81,
  "confidence_score": 74,
  "engagement_score": 83,
  "stress_level": 22,
  "overall_score": 77
}
```

### Expected Feedback Output

```json
{
  "strengths": [
    "Strong distributed systems knowledge with production examples",
    "Clear, structured communication throughout"
  ],
  "improvements": [
    "Add CAP theorem specifics when discussing consistency trade-offs",
    "Include concrete latency numbers in system design answers"
  ],
  "technicalGaps": [
    "Raft vs Paxos consensus – surface-level only",
    "Kubernetes autoscaling (HPA vs VPA) not addressed"
  ],
  "communicationTips": [
    "Reduce filler words – 6 instances detected",
    "Pause 1-2s before answering system design questions"
  ]
}
```

---

## 🧰 Tech Stack

### Backend
| Library | Version | Purpose |
|---|---|---|
| FastAPI | 0.115 | Async REST API framework |
| Uvicorn | 0.30 | ASGI server |
| SQLAlchemy | 2.0 | Async ORM |
| aiosqlite / asyncpg | latest | SQLite / PostgreSQL async drivers |
| httpx | 0.27 | Async HTTP client for Groq API |
| librosa | 0.11 | Audio signal processing |
| PyJWT | 2.9 | JWT token generation and validation |
| python-docx / PyPDF2 | latest | Resume parsing |
| pydantic | 2.9 | Request/response validation |

### Frontend
| Library | Version | Purpose |
|---|---|---|
| React | 18.3 | UI framework |
| TypeScript | 5.5 | Type safety |
| Vite | 5.4 | Build toolchain |
| Zustand | 4.5 | Lightweight state management |
| Recharts | 2.12 | Analytics radar chart and graphs |
| Tailwind CSS | 3.4 | Utility-first styling |
| lucide-react | 0.441 | Icon library |

### AI & ML
| Service | Purpose |
|---|---|
| Groq (llama-3.1-8b-instant) | Question generation, answer evaluation, resume parsing, feedback |
| MediaPipe Tasks | Face and pose landmark detection for visual intelligence |
| Web Speech API | Browser-native STT and TTS for voice interview |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes and add tests
4. Run the test suite: `cd backend && pytest tests/ -v`
5. Commit: `git commit -m "feat: describe your change"`
6. Push and open a pull request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
Built with ❤️ using FastAPI · React · Groq · MediaPipe
<br/>
<a href="https://ai-interviewer-7w1u.onrender.com/login">🌐 Live Demo</a>
</div>
