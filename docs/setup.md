# Setup Guide

## Requirements
- Windows 11 / WSL2
- Python 3.11+
- Node.js 20+
- Local Qwen 14B endpoint (e.g., via LMStudio or Ollama)

## Backend Setup
```bash
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt
uvicorn apps.api.main:app --reload
```

## Frontend Setup
```bash
cd apps/dashboard
npm install
npm run dev
```

Visit `http://localhost:3000` to view the Command Center.
