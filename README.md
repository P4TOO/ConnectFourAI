# ConnectFourAI

A web-based Connect Four game featuring AI opponents powered by Minimax with Alpha-Beta Pruning and Monte Carlo Tree Search (MCTS). Built with Python and React, the project offers adjustable difficulty levels, interactive gameplay, and performance comparisons between AI algorithms.

## Tech Stack

- **Frontend:** React, JavaScript, Vite
- **Backend:** Python 3.11, FastAPI, Uvicorn
- **Testing:** Pytest, HTTPX

## Prerequisites

Make sure the following are installed:

- Python 3.11
- Node.js 20.19+ and npm
- Git

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ConnectFourAI
```

### 2. Backend Setup

Navigate to the backend:

```bash
cd backend
```

Create and activate a virtual environment:

**Windows (PowerShell)**

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

Install Python dependencies:

```bash
python -m pip install -r requirements.txt
```

Start the backend server:

```bash
python -m uvicorn app.main:app --reload
```

Backend: http://127.0.0.1:8000

API Docs: http://127.0.0.1:8000/docs

### 3. Frontend Setup

Open a new terminal from the repository root:

```bash
cd frontend
npm ci
npm run dev
```

Frontend: http://localhost:5173

**Note:** Both servers must run in separate terminals during development.

## Running Tests

From the `backend` directory with the virtual environment activated:

```bash
python -m pytest -v
```

## Project Structure

```text
ConnectFourAI/
├── backend/          # Python API and AI logic
│   ├── app/
│   ├── tests/
│   └── requirements.txt
├── frontend/         # React application
├── .gitignore
└── README.md
```

## Team

- **R01:** Diego Salas
- **R02:** April Perez
- **R03:** Jose Hidalgo

**CPSC 481 — Artificial Intelligence | Fall 2026**
