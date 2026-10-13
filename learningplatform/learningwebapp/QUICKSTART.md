# Quick Start Guide

Get up and running with the Learning Tools platform in 5 minutes!

## Step 1: Install Dependencies

```bash
cd learningwebapp
pip install -r requirements.txt
```

Expected output:
```
Successfully installed Flask-3.0.0 Flask-Login-0.6.3 Flask-CORS-4.0.0 Werkzeug-3.0.1 requests-2.31.0
```

## Step 2: Start the Platform

### Windows:
```cmd
start_with_api.bat
```

### Linux/Mac:

Terminal 1 (API):
```bash
cd ../learningtools
python api.py
```

Terminal 2 (WebApp):
```bash
cd learningwebapp
python app.py
```

You should see:
```
Starting Learning Tools API...
API will be available at: http://localhost:5001
 * Running on http://0.0.0.0:5001

Starting Learning Tools Web Application...
Web app will be available at: http://localhost:5000
 * Running on http://0.0.0.0:5000
```

## Step 3: Register Your Account

1. Open browser to: **http://localhost:5000**
2. Click **"Register"**
3. Enter:
   - Username: `testuser`
   - Password: `password123`
   - Email: `test@example.com` (optional)
4. Click **"Register"**

## Step 4: Login

1. Enter your credentials
2. Click **"Login"**
3. You'll see the dashboard with available workbooks

## Step 5: Start Your First Exercise

1. Find **"JsonPreprocessor.Comments"** workbook
2. Click **"Start Learning"**
3. Read the markdown instructions
4. Find the first code cell
5. Edit the code
6. Click **"Run"** (or press Shift+Enter)
7. See the output below the cell

### Example First Exercise:

```python
from learningtools import *
activate("JsonPreprocessor.Comments")

# See the lesson content
lesson
```

**Expected output:**
```
# JSONP Comments

In this lesson you will learn about...
[Full lesson content displayed]
```

## Step 6: Complete an Exercise

Scroll to an exercise cell:

```python
# Exercise: Parse JSON with comments
content = '''
{
  // This is a comment
  "key": "value"
}
'''

# Your code here
json_object = CJsonPreprocessor(syntax="python").json_loads(content)
p1.check()
```

✅ **Success output:**
```
Correct! You successfully parsed JSON with comments.
```

## Step 7: Check Your Progress

1. Click **"Back to Dashboard"**
2. See your progress updated
3. Continue to next workbook!

## 🎯 What's Next?

- Try other workbooks (RobotFrameworkAIO, etc.)
- Use hints if you get stuck: `p1.hint()`
- View solutions: `p1.solution()`
- Track your progress on the dashboard

## 🛠️ Troubleshooting

### API not connecting?

Check if API is running:
```bash
curl http://localhost:5001/api/health
```

Should return:
```json
{"status":"ok","service":"learningtools-api"}
```

### Can't run code?

Make sure:
1. Both servers are running (ports 5000 and 5001)
2. You're logged in
3. API is accessible (check browser console for errors)

### Module not found?

Ensure learningtools is in the correct directory:
```
RobotFramework_AIO/
  ├── learningtools/      ← Here
  │   ├── api.py
  │   └── ...
  └── learningwebapp/
      ├── app.py
      └── ...
```

## 📚 Learn More

- [README.md](README.md) - Full documentation
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - API reference
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture (JupyterLab version)

## 🎉 You're All Set!

You're now ready to start learning. Happy coding!

---

**Need help?** Check the troubleshooting section in [README.md](README.md#troubleshooting)
