# Dashboard Setup & Running Guide

## Overview

The Callbot Dashboard is a modern, full-stack web application consisting of:
- **Frontend:** React 19 with TypeScript, Vite, and Tailwind CSS
- **Backend:** FastAPI with async PostgreSQL support
- **Database:** PostgreSQL

This guide will help you set up and run the entire application.

---

## Prerequisites

Before starting, ensure you have installed:
- **Node.js 18+** (for frontend)
- **Python 3.10+** (for backend)
- **PostgreSQL 14+** (database)
- **Git** (version control)

Verify installations:
```bash
node --version
python --version
psql --version
```

---

## Part 1: Database Setup

### 1.1 Create Database

Open PostgreSQL and run:

```sql
-- Create database
CREATE DATABASE callbot_db OWNER postgres;

-- Create user (if not exists)
CREATE USER callbot WITH PASSWORD 'callbot_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE callbot_db TO callbot;
GRANT USAGE ON SCHEMA public TO callbot;
GRANT CREATE ON SCHEMA public TO callbot;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO callbot;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO callbot;
```

### 1.2 Load Schema and Sample Data

If you have a `seed.sql` file, load it:

```bash
cd Dashboard/backend/database
psql -U postgres -d callbot_db -f seed.sql
```

This will create:
- Tables (callbot_interactions, etc.)
- Views (v_active_interactions, v_pending_handoffs, v_daily_stats)
- Sample data

### 1.3 Verify Database Connection

```bash
psql -U callbot -d callbot_db -c "SELECT COUNT(*) FROM callbot_interactions;"
```

You should see a count of interactions in the database.

---

## Part 2: Backend Setup

### 2.1 Install Python Dependencies

```bash
cd Dashboard/backend
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2.2 Configure Environment Variables

The `.env` file should be present. Verify it contains:

```env
DATABASE_URL=postgresql+asyncpg://callbot:callbot_password@localhost:5432/callbot_db
CORS_ORIGINS=http://localhost:5173
```

**Important:** The `DATABASE_URL` must use `postgresql+asyncpg` for async support.

### 2.3 Test Backend Connection

```bash
python -c "from app.core.db import engine; print('Database connection OK')"
```

---

## Part 3: Frontend Setup

### 3.1 Install Node Dependencies

```bash
cd Dashboard
npm install
```

### 3.2 Configure Environment Variables

The `.env` file should contain:

```env
VITE_API_URL=http://localhost:8000/api
```

---

## Part 4: Running the Application

### Terminal 1: Start PostgreSQL

Ensure PostgreSQL is running (platform-specific):

**Windows (using Services):**
- Right-click Computer → Manage → Services → Find PostgreSQL → Start

**macOS (if installed via Homebrew):**
```bash
brew services start postgresql
```

**Linux (systemd):**
```bash
sudo systemctl start postgresql
```

**Verify:**
```bash
psql -U postgres -c "SELECT 1;"
```

### Terminal 2: Start Backend API

```bash
cd Dashboard/backend

# Activate venv (if not already activated)
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start FastAPI server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**Test backend:**
```bash
curl http://localhost:8000/health
# Should return: {"status":"ok","service":"Callbot Monitoring API"}
```

### Terminal 3: Start Frontend Dev Server

```bash
cd Dashboard

# Start Vite dev server
npm run dev
```

Expected output:
```
  VITE v7.2.4  ready in 123 ms
  ➜  Local:   http://localhost:5173/
```

### Terminal 4: Open Browser

Open your browser and navigate to:
```
http://localhost:5173
```

You should see the Callbot Dashboard loading with real data from the database!

---

## API Endpoints Reference

All endpoints are under `http://localhost:8000/api`

### Health Check
- `GET /health` - Server health status

### Interactions
- `GET /interactions` - List all interactions with filters
  - Query params: `limit`, `offset`, `status`, `channel`
- `GET /interactions/{id}` - Get specific interaction

### Views (Pre-calculated Statistics)
- `GET /views/active-interactions` - Active interactions
- `GET /views/pending-handoffs` - Pending handoffs
- `GET /views/daily-stats` - Daily statistics
- `GET /views/statistics/summary` - Overall summary
- `GET /views/statistics/by-intent` - Stats by intent
- `GET /views/statistics/by-channel` - Stats by channel

**Example Request:**
```bash
curl "http://localhost:8000/api/interactions?limit=10&status=completed"
```

---

## Frontend Routes

The dashboard has the following main sections (accessible via sidebar):

1. **Overview** - Overall metrics and trends
2. **Agent Performance** - Individual agent statistics
3. **Conversation Quality** - Quality analysis of conversations
4. **Customer Experience** - Customer satisfaction metrics
5. **Operations** - System-wide operational metrics

---

## Common Issues & Solutions

### Issue: "Connection refused" to database
**Solution:** Verify PostgreSQL is running and credentials in `.env` are correct
```bash
psql -U callbot -d callbot_db -c "SELECT 1;"
```

### Issue: "Module not found: FastAPI"
**Solution:** Ensure virtual environment is activated and requirements installed
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: "Cannot find module '@vitejs/plugin-react'"
**Solution:** Reinstall node modules
```bash
rm -rf node_modules package-lock.json
npm install
```

### Issue: "CORS error" when frontend calls backend
**Solution:** Ensure `CORS_ORIGINS` in backend `.env` matches frontend URL
```env
CORS_ORIGINS=http://localhost:5173
```

### Issue: Port 8000 or 5173 already in use
**Solution:** Specify different ports
```bash
# Backend on different port
python -m uvicorn app.main:app --port 8001

# Frontend on different port
npm run dev -- --port 5174
```

---

## Development Tips

### Hot Reload
- **Frontend:** Changes to React/TypeScript code auto-reload in browser
- **Backend:** Use `--reload` flag with uvicorn for auto-reload

### Debug Backend
Add print statements or use Python debugger:
```python
import pdb; pdb.set_trace()
```

### View API Docs
FastAPI automatically generates interactive API docs:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Mock Data
To test without real database data, the frontend includes mock data in `src/data/mockData.ts`.
Modify `src/App.tsx` to use mock data instead of API:
```typescript
// Use mock data instead of API call
setInteractions(mockInteractions);
```

---

## Deployment

### Build Frontend
```bash
cd Dashboard
npm run build
```

Creates optimized build in `dist/` folder.

### Build Docker Images (Optional)

**Frontend Dockerfile:**
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 5173
CMD ["npm", "run", "preview"]
```

**Backend Dockerfile:**
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

---

## Project Structure

```
Dashboard/
├── src/                          # React frontend
│   ├── App.tsx                   # Main component
│   ├── main.tsx                  # Entry point
│   ├── api/
│   │   └── client.ts            # API client
│   ├── types/
│   │   └── dashboard.ts         # TypeScript types
│   ├── components/
│   │   ├── Sidebar.tsx
│   │   ├── Chart.tsx
│   │   ├── MetricCard.tsx
│   │   └── sections/            # Dashboard sections
│   └── data/
│       └── mockData.ts          # Mock data for testing
├── backend/                      # FastAPI backend
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── api/
│   │   │   ├── route.py         # Route aggregation
│   │   │   ├── interactions.py  # Interactions endpoints
│   │   │   └── views.py         # Views endpoints
│   │   └── core/
│   │       ├── config.py        # Settings
│   │       └── db.py            # Database setup
│   ├── .env                     # Environment variables
│   └── requirements.txt         # Python dependencies
├── package.json                 # Node dependencies
├── vite.config.ts              # Vite configuration
├── tsconfig.json               # TypeScript configuration
└── README.md                   # This file
```

---

## Troubleshooting Checklist

- [ ] PostgreSQL is running
- [ ] Database `callbot_db` exists with proper schema
- [ ] Backend `.env` has correct `DATABASE_URL`
- [ ] Frontend `.env` has correct `VITE_API_URL`
- [ ] Backend virtual environment is activated
- [ ] All Python packages installed (`pip list`)
- [ ] All Node packages installed (`npm list`)
- [ ] No port conflicts (8000, 5173)
- [ ] CORS is properly configured
- [ ] Firewall not blocking connections

---

## Support

For issues:
1. Check the `VALIDATION_REPORT.md` for known issues and fixes
2. Review server logs (terminal output)
3. Check browser console (F12 → Console tab)
4. Verify network requests (F12 → Network tab)

---

## Next Steps

1. ✅ Run the application using instructions above
2. ✅ Verify all dashboard sections load correctly
3. ✅ Test filtering and interactions
4. ✅ Monitor logs for any errors
5. ✅ Customize components as needed
6. ✅ Deploy to production environment

**Status:** Dashboard ready for testing and deployment! 🎉
