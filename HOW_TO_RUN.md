# 🚀 How to Run the Courtroom Scheduling System

## ✅ **GOOD NEWS: Your System is Already Running!**

Both servers are currently running:
- ✅ **Backend API**: http://localhost:8000
- ✅ **Frontend**: http://localhost:3001

---

## 📱 **Step 1: Open the Application**

1. **Open your web browser** (Chrome, Firefox, Edge, etc.)
2. **Go to this address**: 
   ```
   http://localhost:3001
   ```
3. You should see the **Login Page** of the Courtroom Scheduling System

---

## 👤 **Step 2: Create Your First User**

Since the database is empty, you need to create a user first.

### **Option A: Using API Documentation (Easiest)**

1. **Open a new browser tab** and go to:
   ```
   http://localhost:8000/docs
   ```

2. **Find the "Authentication" section** and click on:
   ```
   POST /api/auth/register
   ```

3. **Click "Try it out"** button

4. **Copy and paste this JSON** into the Request body:
   ```json
   {
     "email": "admin@court.gov",
     "password": "password123",
     "full_name": "Admin User",
     "role": "court_administrator",
     "court_id": null
   }
   ```

5. **Click "Execute"** button

6. You should see a success response with status code **200**

### **Option B: Using PowerShell Command**

Open PowerShell and run:
```powershell
curl -X POST "http://localhost:8000/api/auth/register" -H "Content-Type: application/json" -d '{\"email\":\"admin@court.gov\",\"password\":\"password123\",\"full_name\":\"Admin User\",\"role\":\"court_administrator\"}'
```

---

## 🔐 **Step 3: Login to the Application**

1. **Go back to**: http://localhost:3001

2. **Enter your credentials**:
   - **Email**: `admin@court.gov`
   - **Password**: `password123`

3. **Click "Sign in"**

4. **You're in!** 🎉 You should now see the Dashboard

---

## 🎯 **Step 4: Explore the Features**

Once logged in, you can explore:

### **Dashboard** (Home Page)
- View statistics
- See recent cases
- Check today's hearings

### **Cases** (Left Sidebar)
- View all cases
- Search and filter cases
- Click on a case to see details

### **Judges** (Left Sidebar)
- View judge profiles
- Check workload and availability
- See specializations

### **Calendar** (Left Sidebar)
- View weekly schedule
- See upcoming hearings
- Check courtroom availability

### **Scheduling** (Left Sidebar)
- Schedule new hearings
- Find available time slots
- View scheduling metrics

### **Documents** (Left Sidebar)
- Search legal documents
- Upload new documents
- Verify document authenticity

---

## 🛑 **If You Need to Stop the Servers**

### **Stop Backend Server:**
```powershell
# Find the process
netstat -ano | findstr :8000

# Kill it (replace <PID> with the actual number)
taskkill /F /PID <PID>
```

### **Stop Frontend Server:**
```powershell
# Find the process
netstat -ano | findstr :3001

# Kill it (replace <PID> with the actual number)
taskkill /F /PID <PID>
```

---

## 🔄 **If You Need to Restart the Servers**

### **Start Backend:**
1. Open PowerShell
2. Navigate to backend folder:
   ```powershell
   cd D:\Dev_WEB\backend
   ```
3. Run:
   ```powershell
   python main.py
   ```

### **Start Frontend:**
1. Open a **NEW** PowerShell window
2. Navigate to project folder:
   ```powershell
   cd D:\Dev_WEB
   ```
3. Run:
   ```powershell
   npm run dev
   ```

---

## 🎨 **Create More Test Users**

You can create different types of users for testing:

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

## 📊 **Available User Roles**

- **court_administrator** - Full access to manage everything
- **chief_justice** - Highest judicial authority
- **presiding_judge** - Judge with case assignment powers
- **scheduler** - Can schedule hearings
- **lawyer** - Can file cases and view assigned cases
- **public_prosecutor** - Prosecution cases
- **litigant** - Limited case viewing
- **public** - Public case search only

---

## 🔍 **Quick Troubleshooting**

### **Problem: Can't access http://localhost:3001**
**Solution**: Check if frontend is running:
```powershell
netstat -ano | findstr :3001
```
If nothing shows, restart the frontend server.

### **Problem: Can't access http://localhost:8000**
**Solution**: Check if backend is running:
```powershell
netstat -ano | findstr :8000
```
If nothing shows, restart the backend server.

### **Problem: Login not working**
**Solution**: 
1. Make sure you created a user first (Step 2)
2. Check the email and password are correct
3. Check backend logs for errors

### **Problem: Database connection error**
**Solution**: 
1. Make sure PostgreSQL is running
2. Run the connection test:
   ```powershell
   python test_connection.py
   ```

---

## 📞 **Need Help?**

### **Check API Documentation:**
http://localhost:8000/docs

### **Check Backend Health:**
http://localhost:8000/health

### **Test Database Connection:**
```powershell
python test_connection.py
```

---

## 🎊 **You're All Set!**

Your Courtroom Scheduling System is ready to use!

**Current Status:**
- ✅ Backend running on port 8000
- ✅ Frontend running on port 3001
- ✅ PostgreSQL database connected
- ✅ Redis cache connected
- ✅ All features implemented

**Just open your browser and go to:**
```
http://localhost:3001
```

Happy scheduling! ⚖️