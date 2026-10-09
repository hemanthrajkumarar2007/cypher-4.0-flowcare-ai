# BedFlow-AI (FlowCare AI)

> **Hospital Operations Intelligence & Bottleneck Resolution Agent**  
> Built for the **Cypher 2026 Hackathon** | Challenge: **"The Blocked Bed"**  
> Fictional Demonstration Hospital: **Sanjeevani Multispeciality Hospital**

---

## 🏥 Project Overview

In acute multispeciality hospitals, bed congestion is rarely just a bed shortage problem—it is a cascading operational bottleneck:
1. **Upstream Bed Blocks**: Inpatients clinically fit for discharge remain in beds awaiting administrative clearance (Third-Party Administrator insurance billing approvals, physician discharge summary signatures, or take-home pharmacy counseling).
2. **Intake Paralysis**: With emergency beds physically blocked, newly arrived triage patients cannot be placed into care cubicles, causing emergency waiting times to surge.
3. **Delayed Diagnostics**: STAT lab and imaging reports face turnaround delays, preventing clinicians from deciding whether observation patients should be admitted or safely sent home.
4. **Shift Handover Deficits**: Imbalanced rostering leaves incoming shifts skeletal, creating severe care bottlenecks.

**BedFlow-AI** connects evidence across disparate hospital datasets, ranks issues transparently by urgency and impact, generates actionable recommendations, and queues simulated tasks for authorized staff review with an immutable audit log.

> **Clinical Safeguard Notice:** BedFlow-AI is strictly an operational decision-support tool. It does **not** make clinical diagnoses, modify patient prescriptions, or execute automated real-world hospital actions.

---

## 🏛️ Project Architecture

```text
BedFlow-AI/
├── backend/                         # FastAPI Backend Service (Python 3.11+)
│   ├── main.py                      # FastAPI app with OpenAPI docs & CORS
│   ├── models.py                    # Pydantic schemas for hospital entities & bottlenecks
│   ├── requirements.txt             # Backend dependencies
│   ├── verify_endpoints.py          # Automated API test suite
│   ├── data/
│   │   └── synthetic_hospital_data.json # 8 connected hospital data categories
│   ├── services/
│   │   ├── data_service.py          # Relational validation engine
│   │   ├── detection_service.py     # 8 core operational problem detectors
│   │   ├── priority_service.py      # Operational priority scoring (0-100)
│   │   ├── causal_service.py        # Cross-domain causal reasoning engine
│   │   ├── recommendation_service.py# Actionable recommendations
│   │   └── action_service.py        # Task review lifecycle & audit trail
│   └── tests/                       # 30 automated Pytest test cases
├── frontend/                        # React + TypeScript + Vite Command Center
│   ├── index.html                   # HTML entrypoint
│   ├── package.json                 # Frontend dependencies (React 18, Vite 6, Lucide)
│   ├── vite.config.ts               # Vite configuration with proxy to backend
│   └── src/
│       ├── App.tsx                  # Master application component & router
│       ├── types.ts                 # TypeScript domain interfaces
│       ├── services/api.ts          # Centralized API client with fallback
│       ├── components/              # Sidebar, Header, Badges, Modals, StatCards
│       └── pages/                   # 10 dedicated command center views
├── start_flowcare.bat               # One-click Windows launcher for both services
└── README.md
```

---

## 🚀 Quick Start (Local Development)

### 1. One-Click Launcher (Windows)
Double-click `start_flowcare.bat` in the root folder. It starts both the FastAPI backend and Vite frontend, then opens `http://localhost:5173`.

### 2. Manual Startup

**Terminal 1 — Backend (FastAPI):**
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
- Interactive Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

**Terminal 2 — Frontend (Vite + React):**
```powershell
cd frontend
pnpm install
pnpm dev
```
- Web Application: [http://localhost:5173](http://localhost:5173)

---

## 🧪 Testing

Run backend automated tests:
```powershell
cd backend
.\.venv\Scripts\pytest -v
```
All **30 tests** pass covering referential integrity, all 8 problem types, causal link generation, priority scoring, and action review workflows.

Verify all API endpoints return HTTP 200 OK:
```powershell
cd backend
.\.venv\Scripts\python verify_endpoints.py
```
