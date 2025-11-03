# 🚀 Quick Start Guide

Get the Superclaims Backend running in 5 minutes!

## Prerequisites
- Python 3.11+
- Google Gemini API key ([Get it here](https://makersuite.google.com/app/apikey))

## Setup Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

Notes:
- The app automatically loads variables from `.env` (via `python-dotenv`).
- Keep `.env` in the project root: `HealthPay Backend Developer Assignment/.env`.

### 3. Run the Server
```bash
uvicorn app.main:app --reload
```

If you run from the repository root, point to the app directory:
```bash
uvicorn app.main:app --reload --app-dir "HealthPay Backend Developer Assignment"
```

### Windows (PowerShell) helper

Run this script as Administrator to free port 8000 and start the server:

```powershell
cd "C:\Users\user\OneDrive\Desktop\assignments\Superclaims-Assignment\HealthPay Backend Developer Assignment"
./start-uvicorn.ps1
```

Server starts at: `http://localhost:8000`

## Test the API

### Using cURL
```bash
curl -X POST "http://localhost:8000/process-claim" \
  -F "files=@your_bill.pdf" \
  -F "files=@discharge_summary.pdf" \
  -F "files=@id_card.pdf"
```

### Using API Docs
Visit: `http://localhost:8000/docs` for interactive Swagger UI

## Quick Docker Setup

### Option A: Docker CLI
```bash
# Build (API key optional at build time; recommended to inject at run time)
docker build -t superclaims-backend .

# Run (recommended: pass API key at runtime)
docker run --rm -p 8000:8000 -e GEMINI_API_KEY=YOUR_KEY superclaims-backend

# Health check
curl http://localhost:8000/health
```

### Option B: docker-compose
Create/update `docker-compose.yml` to include an environment variable:
```yaml
services:
  api:
    build: .
    image: superclaims-backend
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
```
Then:
```bash
GEMINI_API_KEY=YOUR_KEY docker-compose up --build
```

## Project Structure Overview

```
app/
├── main.py              # FastAPI app with /process-claim endpoint
├── graph.py             # LangGraph orchestration
├── agents/              # Specialized processing agents
│   ├── classifier.py    # Classifies documents
│   ├── extractor.py     # Extracts PDF text
│   ├── bill_agent.py    # Processes bills
│   ├── discharge_agent.py
│   ├── id_card_agent.py
│   └── validator.py     # Validates & decides
├── models/
│   └── schemas.py       # Pydantic data models
└── utils/
    ├── gemini_client.py # Gemini API wrapper
    ├── pdf_handler.py   # PDF utilities
    └── prompts.py       # LLM prompt templates
```

## What Happens When You Upload Files?

1. **Extract** → PDFs → Text
2. **Classify** → Identify doc types (bill, discharge, ID card)
3. **Process** → Extract structured data per type
4. **Validate** → Check completeness & consistency
5. **Decide** → Approve/Reject with reasoning

## Common Issues

**Issue**: `GEMINI_API_KEY not set`
- **Fix**: Add your API key to `.env` file (auto-loaded) or pass `-e GEMINI_API_KEY=...` when using Docker.

**Issue**: `ModuleNotFoundError: No module named 'app'`
- **Fix**: Run commands inside the `HealthPay Backend Developer Assignment` directory, or use `--app-dir "HealthPay Backend Developer Assignment"`.

**Issue**: PDF extraction fails
- **Fix**: Ensure PDFs are text-based (not scanned images)

**Issue**: Slow response
- **Fix**: Normal! Processing 3-4 docs takes 8-15 seconds due to LLM calls

## Next Steps

1. ✅ Review `README.md` for full documentation
2. ✅ Check `app/utils/prompts.py` for LLM prompts used
3. ✅ Review agent implementations in `app/agents/`
4. ✅ Test with sample documents from assignment

## Support

For questions about the assignment implementation, refer to:
- **README.md** - Complete documentation
- **Code comments** - Inline documentation
- **Architecture section** - Design decisions

---

**Ready to process claims with AI! 🎉**