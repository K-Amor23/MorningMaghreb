# Casablanca Insights - Startup Guide

## 🚀 Confirmed Working Server Configuration

### Backend (FastAPI)
- **Entrypoint**: `main:app`
- **Command**: `uvicorn main:app --reload --host 127.0.0.1 --port 8000`
- **Health Check**: `http://localhost:8000/health` → `{"status":"healthy","version":"2.0.0"}`
- **Docs**: `http://localhost:8000/docs`
- **Status**: ✅ Running successfully

### Frontend (Next.js)
- **Version**: 15.3.5
- **Command**: `npm run dev` (from `apps/web/`)
- **URL**: `http://localhost:3000`
- **Health Check**: `GET /` → `200 OK`
- **Status**: ✅ Running successfully

## 🔧 Startup Commands

### Quick Start (Both Servers)
```bash
# Terminal 1 - Backend
cd apps/backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2 - Frontend
cd apps/web
npm run dev
```

### Individual Server Start
```bash
# Backend only
cd apps/backend && uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Frontend only
cd apps/web && npm run dev
```

## 📦 Dependency Handling Rules

### Backend Dependencies
- **Core**: `uvicorn`, `fastapi`, `python-dotenv`, `sqlalchemy`, `psycopg2-binary`
- **Optional**: `openai` (for AI features)
- **Install**: `pip install -r requirements.txt` (from `apps/backend/`)

### Frontend Dependencies
- **Core**: `next`, `react`, `react-dom`, `@supabase/supabase-js`
- **Install**: `npm install` (from `apps/web/`)

## 🧠 "Basic Mode" Fallback Behavior

### Backend Basic Mode
- **Trigger**: Missing `OPENAI_API_KEY` or failed external service initialization
- **Behavior**: 
  - Conditional router imports (ETL, moderation disabled)
  - AI features return fallback content
  - Core market data and auth features remain functional
  - Public watchlist API endpoints available without authentication
  - Logs: `"Running in basic mode with limited routers"`

### Frontend Basic Mode
- **Trigger**: Missing Supabase configuration
- **Behavior**: 
  - Auth features disabled
  - Core market data display remains functional
  - Watchlist uses public API endpoints instead of Supabase
  - Graceful degradation of premium features

## 🛠️ Error Handling Policy

### Backend Errors
1. **Read the actual traceback immediately**
2. **Stop spinning on "Running command..." or "Generating..."**
3. **Check for missing dependencies first**
4. **Retry only if cause is clear and fixable**
5. **Use conditional imports to maintain basic functionality**

### Frontend Errors
1. **Check TypeScript compilation errors**
2. **Verify all imported components exist**
3. **Check for missing environment variables**
4. **Restart development server if needed**

## ❌ Strict Rules (Never Violate)

### Do NOT:
- Create new test scripts like `test_server.py`, `run_dev.py`, etc.
- Reinstall packages without explicit permission
- Modify environment or dependencies unless asked
- Use different entrypoints than confirmed working ones
- Generate new server files or startup scripts

### DO:
- Use only the confirmed working commands above
- Read error logs before attempting fixes
- Maintain the established project structure
- Follow the "basic mode" fallback strategy

## 🔍 Health Checks

### Backend Health
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy","version":"2.0.0","timestamp":"..."}
```

### Frontend Health
```bash
curl -I http://localhost:3000
# Expected: HTTP/1.1 200 OK
```

## 📁 Project Structure
```
Casablanca-Insights/
├── apps/
│   ├── backend/          # FastAPI server
│   │   ├── main.py       # Entry point
│   │   ├── routers/      # API routes
│   │   └── requirements.txt
│   └── web/              # Next.js frontend
│       ├── pages/        # Next.js pages
│       ├── components/   # React components
│       └── package.json
├── .env                  # Environment variables
└── cursor_startup.md     # This file
```

## 🚨 Troubleshooting

### Port Already in Use
```bash
# Kill processes on ports
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

### Missing Dependencies
```bash
# Backend
cd apps/backend && pip install -r requirements.txt

# Frontend
cd apps/web && npm install
```

### Environment Variables
- Ensure `.env` file exists in project root
- `OPENAI_API_KEY` is optional (enables AI features)
- `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` for auth

## 📚 Documentation Links
- **API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000
- **Health Check**: http://localhost:8000/health

---
**Last Updated**: January 2024
**Status**: ✅ Both servers confirmed working
**Version**: Casablanca Insights v2.0.0 