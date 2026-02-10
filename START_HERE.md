# 🚀 START HERE - Quick Start Guide

## ✅ YOUR SYSTEM IS ALREADY RUNNING!

Both servers are currently running:
- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:3001

---

## 📱 **STEP 1: Open the Application**

1. **Open your web browser** (Chrome, Firefox, Edge, etc.)
2. **Go to**: http://localhost:3001
3. You should see the **Login Page**

---

## 👤 **STEP 2: Create Your First User**

Since this is a fresh database, you need to create a user first.

### **Option A: Using the Browser (Easiest)**

1. **Open a new browser tab**
2. **Go to**: http://localhost:8000/docs
3. **Scroll down** to find "Authentication" section
4. **Click on** `POST /api/auth/register`
5. **Click** "Try it out" button
6. **Copy and paste** this into the Request body box:

```json
{
  "email": "admin@court.gov",
  "password": "password123",
  "full_name": "Admin User",
  "role": "court_administrator",
  "court_id": null
}
```

7. **Click** "Execute" button
8. You should see **"200 Success"** response

### **Option B: Using PowerShell**

Open PowerShell and run:
```powershell
curl -X POST "http://localhost:8000/api/auth/register" -H "Content-Type: application/json" -d '{\"email\":\"admin@court.gov\",\"password\":\"password123\",\"full_name\":\"Admin User\",\"role\":\"court_administrator\"}'
```

---

## 🔐 **STEP 3: Login to the Application**

1. **Go back to**: http://localhost:3001
2. **Enter credentials**:
   - **Email**: `admin@court.gov`
   - **Password**: `password123`
3. **Click** "Sign in"
4. **You're in!** 🎉

---

## 🎯 **STEP 4: Explore the Features**

Once logged in, you can:

### **Dashboard** (Home)
- View system statistics
- See recent cases
- Check today's hearings
- Quick actions

### **Cases** (Left Sidebar)
- View all cases
- Search and filter
- Create new cases
- View case details

### **Judges** (Left Sidebar)
- View judge profiles
- Check workload
- See specializations
- Manage availability

### **Calendar** (Left Sidebar)
- View weekly schedule
- See upcoming hearings
- Check courtroom availability
- Drag-and-drop rescheduling

### **Scheduling** (Left Sidebar)
- Schedule new hearings
- Find available time slots
- View scheduling metrics
- Optimization insights

### **Documents** (Left Sidebar)
- Search legal documents
- Upload new documents
- Verify document authenticity
- Semantic search

---

## 🛑 **IF SERVERS ARE NOT RUNNING**

If you closed the terminals or need to restart:

### **Start Backend Server:**

1. Open PowerShell
2. Navigate to backend folder:
   ```powershell
   cd D:\Dev_WEB\backend
   ```
3. Run:
   ```powershell
   python main.py
   ```
4. You should see: `Uvicorn running on http://0.0.0.0:8000`

### **Start Frontend Server:**

1. Open a **NEW** PowerShell window
2. Navigate to project folder:
   ```powershell
   cd D:\Dev_WEB
   ```
3. Run:
   ```powershell
   npm run dev
   ```
4. You should see: `Local: http://localhost:3001/`

---

## 🔄 **IF YOU NEED TO STOP THE SERVERS**

### **Stop Backend:**
```powershell
# Find the process
netstat -ano | findstr :8000

# Kill it (replace <PID> with the actual number)
taskkill /F /PID <PID>
```

### **Stop Frontend:**
```powershell
# Find the process
netstat -ano | findstr :3001

# Kill it (replace <PID> with the actual number)
taskkill /F /PID <PID>
```

---

## 🎨 **CREATE MORE TEST USERS**

You can create different types of users:

### **Judge User:**
```json
{
  "email": "judge@court.gov",
  "password": "password123",
  "full_name": "Judge Smith",
  "role": "presiding_judge",
  "court_id": null
}
```

### **Lawyer User:**
```json
{
  "email": "lawyer@court.gov",
  "password": "password123",
  "full_name": "Lawyer Johnson",
  "role": "lawyer",
  "court_id": null
}
```

### **Public User:**
```json
{
  "email": "public@example.com",
  "password": "password123",
  "full_name": "Public User",
  "role": "public",
  "court_id": null
}
```

---

## 📊 **AVAILABLE USER ROLES**

- **court_administrator** - Full access (recommended for testing)
- **chief_justice** - Highest judicial authority
- **presiding_judge** - Judge with case assignment powers
- **scheduler** - Can schedule hearings
- **lawyer** - Can file and view cases
- **public_prosecutor** - Prosecution cases
- **litigant** - Limited case viewing
- **public** - Public case search only

---

## 🔍 **QUICK TROUBLESHOOTING**

### **Problem: Can't access http://localhost:3001**
**Solution**: 
```powershell
# Check if frontend is running
netstat -ano | findstr :3001

# If nothing shows, start it:
cd D:\Dev_WEB
npm run dev
```

### **Problem: Can't access http://localhost:8000**
**Solution**:
```powershell
# Check if backend is running
netstat -ano | findstr :8000

# If nothing shows, start it:
cd D:\Dev_WEB\backend
python main.py
```

### **Problem: Login not working**
**Solution**:
1. Make sure you created a user first (Step 2)
2. Check email and password are correct
3. Try creating the user again

### **Problem: Database connection error**
**Solution**:
```powershell
# Test the connection
python test_connection.py

# If it fails, make sure PostgreSQL is running
```

---

## 📞 **USEFUL LINKS**

- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 🎊 **YOU'RE ALL SET!**

**Current Status:**
- ✅ Backend running on port 8000
- ✅ Frontend running on port 3001
- ✅ PostgreSQL database connected
- ✅ Redis cache connected
- ✅ All features implemented
- ✅ All endpoints tested and working

**Just open your browser and go to:**
```
http://localhost:3001
```

**Happy scheduling! ⚖️**

---

## 📚 **ADDITIONAL RESOURCES**

- **Full Setup Guide**: See `SETUP_COMPLETE.md`
- **How to Run**: See `HOW_TO_RUN.md`
- **Endpoint Tests**: See `ENDPOINT_TEST_RESULTS.md`
- **Task Breakdown**: See `courtroom-scheduling-tasks.md`
- **README**: See `README.md`

---

## 💡 **TIPS**

1. **Keep both PowerShell windows open** while using the application
2. **Don't close the terminals** - they're running your servers
3. **Use Chrome DevTools** (F12) to see any frontend errors
4. **Check backend logs** in the PowerShell window for API errors
5. **Use API docs** at http://localhost:8000/docs to test endpoints directly

---

**Need help? Check the troubleshooting section above or review the detailed guides in the project folder.**