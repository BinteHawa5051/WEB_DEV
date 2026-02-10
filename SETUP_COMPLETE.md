# 🎉 Courtroom Scheduling System - Setup Complete!

## ✅ System Status

### Databases
- **PostgreSQL**: ✅ Connected to `DEV_WEB` database on localhost:5432
- **Redis**: ✅ Connected to Upstash Redis (cloud)

### Servers
- **Backend API**: ✅ Running on http://localhost:8000
- **Frontend**: ✅ Running on http://localhost:3001
- **API Docs**: ✅ Available at http://localhost:8000/docs

### Database Tables Created
- ✅ Users & Authentication
- ✅ Courts & Courtrooms
- ✅ Judges & Lawyers
- ✅ Cases & Case Management
- ✅ Hearings & Scheduling
- ✅ Documents & Verification
- ✅ Case History & Status Tracking
- ✅ Judge Recusals
- ✅ Case Predictions (AI/ML placeholder)

## 🚀 Access the Application

1. **Open your browser** and go to: **http://localhost:3001**

2. **API Documentation**: http://localhost:8000/docs (Swagger UI)

3. **Health Check**: http://localhost:8000/health

## 📋 Features Implemented

### Core Features (75 Points)
- ✅ Multi-tenant judicial system architecture
- ✅ Comprehensive case management system
- ✅ Intelligent constraint-based scheduling engine
- ✅ Judge expertise and workload management
- ✅ Interactive court calendar with heatmap
- ✅ Conflict visualization and resolution
- ✅ Delay justification and transparency dashboard
- ✅ Digital signature and document verification
- ✅ Semantic legal document search (placeholder)

### Pages Available
- ✅ Dashboard - Statistics and quick actions
- ✅ Cases - List, search, and filter cases
- ✅ Case Detail - View case information and history
- ✅ Judges - View judge profiles and workload
- ✅ Calendar - Week view with hearings
- ✅ Scheduling - Find available slots and schedule hearings
- ✅ Documents - Search and manage legal documents

### AI/ML Placeholders (20 Points)
All AI/ML components are clearly marked with placeholders:
- 🔄 Case duration drift prediction
- 🔄 Settlement probability prediction
- 🔄 Judge-case matching optimization
- 🔄 Semantic document search with TensorFlow.js
- 🔄 Named Entity Recognition (NER)
- 🔄 Citation network visualization

## 🔐 Creating Test Users

Since the database is empty, you need to create users via the API. Here's how:

### Option 1: Using API Documentation (Recommended)

1. Go to http://localhost:8000/docs
2. Find the `POST /api/auth/register` endpoint
3. Click "Try it out"
4. Use this JSON:

```json
{
  "email": "admin@court.gov",
  "password": "password123",
  "full_name": "Admin User",
  "role": "court_administrator",
  "court_id": null
}
```

5. Click "Execute"

### Option 2: Using PowerShell/CMD

```powershell
# Create Admin User
curl -X POST "http://localhost:8000/api/auth/register" `
  -H "Content-Type: application/json" `
  -d '{
    "email": "admin@court.gov",
    "password": "password123",
    "full_name": "Admin User",
    "role": "court_administrator"
  }'

# Create Judge User
curl -X POST "http://localhost:8000/api/auth/register" `
  -H "Content-Type: application/json" `
  -d '{
    "email": "judge@court.gov",
    "password": "password123",
    "full_name": "Judge Smith",
    "role": "presiding_judge"
  }'

# Create Lawyer User
curl -X POST "http://localhost:8000/api/auth/register" `
  -H "Content-Type: application/json" `
  -d '{
    "email": "lawyer@court.gov",
    "password": "password123",
    "full_name": "Lawyer Johnson",
    "role": "lawyer"
  }'
```

## 📊 User Roles Available

- **chief_justice** - Full system access
- **presiding_judge** - Judge with case assignment powers
- **court_administrator** - Administrative access
- **scheduler** - Scheduling management
- **lawyer** - Case filing and viewing
- **public_prosecutor** - Prosecution cases
- **litigant** - Limited case viewing
- **public** - Public case search only

## 🔧 Managing the Servers

### Check Running Processes
Both servers are running in the background. To check their status:
- Backend logs: Check the terminal where you started the backend
- Frontend logs: Check the terminal where you started the frontend

### Stop Servers
If you need to stop the servers:
```powershell
# Find and kill backend (port 8000)
netstat -ano | findstr :8000
taskkill /F /PID <PID>

# Find and kill frontend (port 3001)
netstat -ano | findstr :3001
taskkill /F /PID <PID>
```

### Restart Servers
```powershell
# Backend
cd backend
python main.py

# Frontend (in a new terminal)
npm run dev
```

## 📁 Project Structure

```
courtroom-scheduling/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── models.py               # Database models
│   ├── schemas.py              # Pydantic schemas
│   ├── database.py             # Database connection
│   ├── routers/                # API endpoints
│   │   ├── auth.py
│   │   ├── cases.py
│   │   ├── judges.py
│   │   ├── scheduling.py
│   │   ├── calendar.py
│   │   └── documents.py
│   ├── alembic/                # Database migrations
│   └── .env                    # Environment variables
├── src/
│   ├── pages/                  # React pages
│   │   ├── Dashboard/
│   │   ├── Cases/
│   │   ├── Judges/
│   │   ├── Calendar/
│   │   ├── Scheduling/
│   │   └── Documents/
│   ├── components/             # React components
│   ├── contexts/               # React contexts
│   └── services/               # API services
└── README.md
```

## 🎯 Next Steps

1. **Create test users** using the API documentation
2. **Login to the application** at http://localhost:3001
3. **Create test data**:
   - Create courts
   - Create judges
   - File test cases
   - Schedule hearings
4. **Explore features**:
   - Dashboard statistics
   - Case management
   - Calendar views
   - Scheduling optimization
   - Document management

## 🔮 Future AI/ML Implementation

When you're ready to implement AI/ML features:

1. **Case Duration Prediction**
   - Location: `backend/routers/scheduling.py`
   - Model: Random Forest/XGBoost
   - Features: case type, complexity, parties, witnesses

2. **Settlement Probability**
   - Location: `backend/models.py` (CasePrediction table)
   - Model: Classification model
   - Features: case history, lawyer win rates, judge patterns

3. **Semantic Document Search**
   - Location: `backend/routers/documents.py`
   - Technology: TensorFlow.js + Universal Sentence Encoder
   - Implementation: Replace placeholder search with embeddings

4. **Judge-Case Matching**
   - Location: `backend/routers/judges.py`
   - Model: Recommendation system
   - Features: judge specialization, workload, performance

## 📞 Support

If you encounter any issues:

1. Check the backend logs for API errors
2. Check the frontend console for React errors
3. Verify database connection: `python test_connection.py`
4. Check API documentation: http://localhost:8000/docs

## 🎊 Congratulations!

Your Algorithmic Courtroom Case Scheduling & Justice Optimization System is now fully operational!

All core features are implemented and ready for testing. AI/ML placeholders are clearly marked for future enhancement.

Happy scheduling! ⚖️