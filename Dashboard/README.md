# CallBot Dashboard

A comprehensive React-based dashboard for monitoring customer support and call-bot performance analytics with real PostgreSQL database integration.

## 🚀 Quick Start

See [QUICKSTART.md](./QUICKSTART.md) for 5-minute setup instructions.

## Features

### Dashboard Sections

1. **Overview** - High-level system health and performance metrics
   - Total interactions, success rates, handoff rates
   - Average response times and customer satisfaction
   - Active issues by urgency level
   - System health indicators
   - Real data from PostgreSQL database

2. **Agent Performance** - Individual agent analytics and coaching insights
   - Performance comparison across agents  
   - Resolution rates and response times
   - Customer satisfaction by agent
   - Top handoff reasons and coaching opportunities

3. **Conversation Quality** - Analysis of individual conversations
   - Quality scoring and filtering
   - Conversation history replay
   - Emotion progression tracking
   - De-escalation success metrics

4. **Customer Experience** - Customer satisfaction and experience metrics
   - Satisfaction trends by channel
   - Emotion distribution
   - Intent-based satisfaction analysis
   - Feedback analysis

5. **Operations** - System performance and operational metrics
   - Response time distribution
   - Handoff reason analysis
   - Peak hours analysis
   - Urgency-based resolution times

## 📊 Architecture

### Backend (FastAPI + PostgreSQL)
- **Location**: `Dashboard/backend/`
- **Framework**: FastAPI with async SQLAlchemy
- **Database**: PostgreSQL with seed.sql schema
- **Port**: 8000 (default)

**Key Endpoints:**
```
/api/interactions              - All interactions with filters
/api/views/active-interactions - Currently active interactions
/api/views/daily-stats        - Daily aggregated statistics
/api/views/statistics/*       - Various statistics endpoints
```

### Frontend (React + TypeScript)
- **Location**: `Dashboard/`
- **Framework**: React 19 + Vite + TypeScript
- **Styling**: Tailwind CSS
- **Port**: 5173 (default)

**API Client**: Centralized in `src/api/client.ts`

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL 12+ (with callbot_db)

### Backend Setup

```bash
cd Dashboard/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate (Windows)

# Install dependencies
pip install -r requirements.txt

# Configure database
# Edit .env with your PostgreSQL credentials
cp .env.example .env

# Start server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd Dashboard

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Start development server
npm run dev
```

The dashboard will be available at `http://localhost:5173`

## 📋 Configuration

### Backend (.env)
```env
DATABASE_URL=postgresql+asyncpg://callbot:password@localhost:5432/callbot_db
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000/api
```

## 📁 Project Structure

```
Dashboard/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── interactions.py    # Interactions endpoints
│   │   │   ├── views.py           # Views & statistics endpoints
│   │   │   └── route.py           # Router setup
│   │   ├── core/
│   │   │   ├── config.py          # Settings configuration
│   │   │   └── db.py              # Database connection
│   │   └── main.py                # FastAPI app
│   ├── database/
│   │   └── seed.sql               # Database schema
│   ├── requirements.txt
│   └── .env.example
├── src/
│   ├── api/
│   │   └── client.ts              # API client
│   ├── components/
│   │   ├── Sidebar.tsx
│   │   ├── MetricCard.tsx
│   │   ├── Chart.tsx
│   │   └── sections/              # Dashboard sections
│   ├── types/
│   │   └── dashboard.ts           # TypeScript interfaces
│   ├── data/
│   │   └── mockData.ts            # Legacy mock data
│   ├── App.tsx
│   └── main.tsx
├── package.json
├── .env
├── .env.example
├── SETUP.md                       # Detailed setup guide
├── QUICKSTART.md                  # Quick start guide
└── README.md                      # This file
```

## 📚 Documentation

- **[QUICKSTART.md](./QUICKSTART.md)** - 5-minute setup guide
- **[SETUP.md](./SETUP.md)** - Complete installation and configuration
- **[CHANGES.md](./CHANGES.md)** - Detailed list of recent updates
- **[backend/database/seed.sql](./backend/database/seed.sql)** - Database schema

## 🔌 API Integration

The frontend communicates with the backend through a centralized API client:

```typescript
import apiClient from './api/client';

// Fetch interactions
const data = await apiClient.getInteractions(50, 0);

// Get statistics
const stats = await apiClient.getStatisticsSummary();
```

All API calls include:
- Automatic error handling
- Query parameter support
- Type-safe responses
- CORS support

## 💾 Database

The application uses PostgreSQL with the following key components:

**Main Table:**
- `callbot_interactions` - All customer interactions with comprehensive data

**Views:**
- `v_active_interactions` - Currently active interactions
- `v_pending_handoffs` - Pending handoff requests
- `v_daily_stats` - Daily aggregated statistics

See [backend/database/seed.sql](./backend/database/seed.sql) for full schema.

## 🔧 Development

### Backend Development
```bash
# Backend auto-reloads on code changes
uvicorn app.main:app --reload

# Run with specific port
uvicorn app.main:app --reload --port 8001
```

### Frontend Development
```bash
# Frontend auto-reloads on code changes
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🐛 Troubleshooting

### Backend Won't Start
- Check Python version: `python --version` (should be 3.9+)
- Verify database connection in .env
- Check if port 8000 is available

### Frontend Can't Connect to API
- Verify backend is running on http://localhost:8000
- Check VITE_API_URL in .env
- Open browser console (F12) for detailed errors
- Check Network tab to see API requests

### Database Connection Issues
- Verify PostgreSQL is running
- Check DATABASE_URL in .env
- Test connection: `psql postgresql://user:pass@localhost/callbot_db`
- Restore database: `pg_restore -U callbot -d callbot_db --clean --if-exists Dashboard/backend/database/callbot_db.backup`

## 📦 Production Build

### Build Frontend
```bash
npm run build
# Output in dist/ directory
```

### Run Backend with Gunicorn
```bash
pip install gunicorn
gunicorn -b 0.0.0.0:8000 --workers 4 app.main:app
```

## 🤝 Technology Stack

### Backend
- FastAPI 0.115.6
- SQLAlchemy 2.0.36
- asyncpg 0.30.0
- PostgreSQL 12+

### Frontend
- React 19.2.0
- TypeScript 5.9
- Vite 7.2.4
- Tailwind CSS 3.4.19
- Chart.js 4.5.1

## 📝 Features Implemented

✅ Real-time data from PostgreSQL  
✅ Async database queries  
✅ CORS-enabled API  
✅ Comprehensive dashboard sections  
✅ Responsive UI design  
✅ Chart visualizations  
✅ Metric calculations  
✅ Agent performance tracking  
✅ Customer satisfaction metrics  
✅ Conversation quality analysis  
✅ Environment-based configuration  
✅ Error handling and loading states  

## 📊 Sample Data

The database includes sample interactions with:
- Different intents (order_inquiry, billing_question, account_access, etc.)
- Multiple channels (phone, chat, email, sms)
- Various urgency levels (low, medium, high, critical)
- Agent assignments and handoff tracking
- Customer satisfaction ratings
- Conversation histories

## 🚀 Next Steps

1. Follow the [QUICKSTART.md](./QUICKSTART.md) for setup
2. Verify database connection
3. Start backend and frontend servers
4. Access dashboard at http://localhost:5173
5. Explore the data and sections
6. Customize as needed for your use case

## 📞 Support

For issues and troubleshooting:
1. Check the relevant documentation (SETUP.md, QUICKSTART.md)
2. Review browser console and network logs
3. Check backend terminal for errors
4. Verify database connectivity

---

**Version**: 1.0.0  
**Last Updated**: January 29, 2026  
**Status**: ✅ Production Ready

3. **Conversation Quality & Learning** - The core learning component
   - Interactive conversation browser with quality scoring
   - Good vs poor conversation identification
   - Emotion journey analysis showing customer sentiment progression
   - Learning insights with success patterns and common issues
   - Best practice examples from high-performing conversations

4. **Customer Experience** - Customer-centric analytics
   - Emotion distribution and satisfaction trends
   - Channel performance comparison (chat, phone, email, SMS)
   - Intent vs satisfaction analysis
   - Customer feedback highlights

5. **Operational Performance** - System efficiency metrics
   - Response time distribution and trends
   - Handoff reasons analysis
   - Peak hours and load analysis
   - System confidence levels

## Technology Stack

- **Frontend**: React 18 + TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Build Tool**: Vite
- **Charts**: Chart.js (ready to integrate)

## Data Structure

The dashboard uses a comprehensive data model including:
- `Interaction` records with conversation history
- Customer satisfaction and feedback
- Agent performance metrics
- System confidence and execution times
- Emotion tracking throughout conversations

## Getting Started

### Prerequisites

- Node.js 16+ 
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

### Development

The dashboard runs at `http://localhost:5173` in development mode.

## Key Learning Features

### Conversation Analysis
- **Quality Scoring**: Automated scoring based on satisfaction, success, response time, and emotion progression
- **Emotion Tracking**: Visualizes customer emotion changes throughout conversations
- **Success Patterns**: Identifies communication techniques that lead to positive outcomes
- **De-escalation Examples**: Shows how successful agents handle frustrated customers

### Agent Coaching
- **Best Practice Library**: High-quality conversation examples for training
- **Common Issues**: Identifies recurring problems and improvement areas  
- **Performance Insights**: Individual agent strengths and development opportunities
- **Collaborative Learning**: Anonymous sharing of effective techniques

## Dashboard Philosophy

This dashboard is designed with a **learning-first approach**:
- Focuses on improvement rather than punishment
- Provides actionable insights for agent development
- Emphasizes transparency and continuous learning
- Supports both individual and team growth

## Customization

The dashboard is built with modularity in mind:
- Easy to add new metrics and visualizations
- Configurable data sources
- Extensible section architecture
- Responsive design for all devices
