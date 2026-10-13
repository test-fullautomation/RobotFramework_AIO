# Learning Tools Web Application

A web-based interactive learning platform for programming exercises with user authentication, progress tracking, and **browser-based code execution**.

## 🌟 Features

- 🔐 **User Authentication** - Secure registration and login system
- 📚 **Multiple Workbooks** - Support for different learning modules
- 📊 **Progress Tracking** - Save and resume your progress
- 💻 **Browser-Based Code Execution** - Write and run code directly in your browser
- ✅ **Interactive Validation** - Instant feedback on your solutions
- 🎯 **Hints & Solutions** - Get help when you need it
- 🚀 **Real-time Output** - See results immediately
- 📱 **Responsive Design** - Works on desktop and mobile

## 🏗️ Architecture

The platform uses a **microservices architecture**:

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Browser   │ ◄─────► │  Flask Web   │ ◄─────► │ Learning    │
│   (User)    │  HTTP   │  App (5000)  │  HTTP   │ Tools API   │
└─────────────┘         └──────────────┘         │   (5001)    │
                                                  └─────────────┘
```

- **Web Application** (Port 5000): User interface, authentication, progress management
- **Learning Tools API** (Port 5001): Code execution engine with sandboxed sessions

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for detailed API reference.

## 📋 Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- Modern web browser (Chrome, Firefox Edge, Safari)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd learningwebapp
pip install -r requirements.txt
```

### 2. Start the Platform

**Windows:**
```cmd
cd learningplatform
start_with_api.bat
```

**Linux/Ubuntu:**
```bash
cd learningplatform
chmod +x start_with_api.sh  # First time only
./start_with_api.sh
```

Both scripts will:
1. Check for Python installation
2. Start the Learning Tools API on port 5001
3. Start the Web Application on port 5000
4. Open your browser automatically
5. Handle graceful shutdown with Ctrl+C

**Manual Start (Alternative):**

Terminal 1:
```bash
cd learningplatform/learningtools
python3 api.py  # or python api.py on Windows
```

Terminal 2:
```bash
cd learningplatform/learningwebapp
python3 app.py  # or python app.py on Windows
```

### 3. Access the Application

Open your browser to: **http://localhost:5000**

### 4. Create an Account

1. Click "Register" on the login page
2. Enter your username and password
3. Log in with your credentials

## 📖 How to Use

### Starting a Workbook

1. **Login** to your account
2. **Dashboard** displays all available workbooks
3. **Click "Start Learning"** on any workbook
4. **Read the instructions** in markdown cells
5. **Write code** in code cells
6. **Click "Run"** or press **Shift+Enter** to execute
7. **View output** below the cell
8. **Progress saves** automatically when you complete exercises

### Code Execution

#### Example Workbook Cell:

```python
from learningtools import *
activate("JsonPreprocessor.Comments")

# Exercise: Parse JSON with comments
content = '''
{
  // This is a comment
  "name": "value"
}
'''

json_object = CJsonPreprocessor(syntax="python").json_loads(content)
p1.check()  # Validate your answer
```

#### Features:
- ▶️ **Run Button**: Execute the code
- 🔄 **Reset Button**: Restore original code
- ⌨️ **Shift+Enter**: Keyboard shortcut to run
- 📤 **Live Output**: See results instantly
- ❌ **Error Display**: Clear error messages with traceback

### Getting Help

- **Hints**: Available for each exercise (click hint button in learningtools output)
- **Solutions**: Full solution code available (click solution button)
- **Progress**: Tracked automatically and synced to dashboard

## 🎨 User Interface

### Dashboard
- View all available workbooks
- Track completion progress
- See progress bars for each module
- Quick access to continue learning

### Workbook Page
- **Markdown cells**: Instructions and explanations
- **Code cells**: Interactive code editors
- **Output panels**: Display results and errors
- **Progress indicator**: Track your completion

## 📁 Project Structure

```
learningplatform/
├── start_with_api.bat         # Windows startup script
├── start_with_api.sh          # Linux/Ubuntu startup script
├── learningtools/             # API service
│   ├── api.py                 # Flask API for code execution
│   ├── core.py                # Learning engine
│   ├── validators.py          # Solution validators
│   ├── examples/              # Exercise notebooks
│   │   ├── JsonPreprocessor/
│   │   └── RobotFrameworkAIO/
│   └── templates/             # Exercise templates
└── learningwebapp/            # Web application
    ├── app.py                 # Main Flask application
    ├── requirements.txt       # Python dependencies
    ├── README.md              # This file
    ├── API_DOCUMENTATION.md   # API reference guide
    ├── templates/             # HTML templates
    │   ├── base.html          # Base template
    │   ├── login.html         # Login page
    │   ├── register.html      # Registration page
    │   ├── dashboard.html     # User dashboard
    │   ├── category.html      # Category listing
    │   └── workbook_execute.html  # Code execution interface
    ├── static/                # Static assets
    │   └── style.css          # Custom styles
└── webapp.db                   # SQLite database (created on first run)
```

## 🔧 Configuration

### Environment Variables

You can customize the application using environment variables:

```bash
# Secret key for session management (REQUIRED in production)
export SECRET_KEY='your-secret-key-here'

# API base URL (if running API on different host/port)
export API_BASE_URL='http://localhost:5001'

# Database path (optional)
export DATABASE='./custom_db.db'
```

### Custom Configuration

Edit `app.py` to modify:
- `app.config['SECRET_KEY']` - Session secret key
- `app.config['API_BASE_URL']` - API server location
- `app.config['DATABASE']` - Database file path

## 🧪 Testing

### Test the API

```bash
# Health check
curl http://localhost:5001/api/health

# List workbooks
curl http://localhost:5001/api/workbooks

# Execute code
curl -X POST http://localhost:5001/api/execute \
  -H "Content-Type: application/json" \
  -d '{"code": "print(2+2)", "workbook_name": "test", "session_id": "test"}'
```

### Test the Web App

1. Register a new user
2. Login with credentials
3. Start a workbook
4. Run code in a cell
5. Check dashboard for updated progress

## 🛠️ Troubleshooting

### Cannot connect to API

**Error**: "Make sure the API server is running on port 5001"

**Solution**:
1. Check if API is running: `curl http://localhost:5001/api/health`
2. Start API manually: `cd ../learningtools && python api.py`
3. Check firewall settings

### Port already in use

**Error**: "Address already in use"

**Solution**:
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :5000
kill -9 <PID>
```

### Module not found

**Error**: "ModuleNotFoundError: No module named 'learningtools'"

**Solution**:
1. Ensure learningtools is in parent directory
2. Check Python path: `sys.path.insert(0, str(BASE_DIR))`

### Database locked errors

**Error**: "sqlite3.OperationalError: database is locked"

**Solution** (Already implemented in current version):
- WAL mode enabled for concurrent access
- Retry logic with exponential backoff
- 30-second timeout configured

**If still occurs:**
```bash
# Remove stale lock files
rm webapp.db-shm webapp.db-wal

# Restart services
./start_with_api.sh  # or start_with_api.bat on Windows
```

### API timeout (30 seconds)

**Error**: Request to API times out after 30 seconds

**Causes** (Already fixed in current version):
- ~~Proxy blocking localhost~~ → Fixed with NO_PROXY environment variable
- ~~Infinite loop in initialization~~ → Fixed with safety limits in notebook cells

**If still occurs:**
- Check for heavy computation in your code
- Verify environment variables are set (check startup logs)

### Proxy issues in corporate networks

**Error**: "Failed to establish connection" or timeouts

**Solution** (Already configured in startup scripts):
```bash
# Windows (start_with_api.bat)
set NO_PROXY=localhost,127.0.0.1,::1

# Linux (start_with_api.sh)
export NO_PROXY="localhost,127.0.0.1,::1"
```

If manual start:
```bash
export NO_PROXY="localhost,127.0.0.1,::1"
export LEARNINGTOOLS_DISABLE_JUPYTER_DETECTION=1
python3 api.py
```

### Progress not showing

**Problem**: Completed exercises but dashboard shows 0 progress

**Solution** (Already implemented):
- Progress automatically syncs during code execution
- Check user workspace exists: `user_workspaces/user_<id>/`
- Verify progress file created: `user_workspaces/user_<id>/.progress/progress.json`

**Manual sync** (if needed):
```python
# In workbook, after p1.check()
lesson.progress()  # Should show completed
```

### User-specific data

**Location of user data:**
```
learningwebapp/user_workspaces/
└── user_<id>/
    ├── .progress/
    │   └── progress.json          # User's progress
    └── <workbook_name>/
        └── practice_files.jsonp   # User's exercise files
```

**Note**: Each user has completely isolated workspace and progress tracking

## 🔐 Security

### Development vs Production

⚠️ **Current implementation is for DEVELOPMENT/EDUCATIONAL USE ONLY**

**Security Issues in Development:**
- Uses `exec()` without sandboxing
- No resource limits (CPU, memory, time)
- Development secret key
- No HTTPS
- In-memory session storage

### Production Recommendations

For production deployment:

1. **Use Docker sandboxing** for code execution
2. **Set secure SECRET_KEY** from environment
3. **Enable HTTPS** (use nginx/Apache reverse proxy)
4. **Add rate limiting** (Flask-Limiter)
5. **Use PostgreSQL** instead of SQLite
6. **Implement session timeouts**
7. **Add CSRF protection**
8. **Restrict code imports**

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md#security-considerations) for detailed security guidance.

## 📚 Documentation

- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Complete API reference
- [QUICKSTART.md](QUICKSTART.md) - Step-by-step tutorial
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture (old JupyterLab version)

## 🚀 Deployment

### Development

```bash
# Both servers
start_with_api.bat
```

### Production (Example with Gunicorn)

```bash
# Install Gunicorn
pip install gunicorn

# Start API
cd learningtools
gunicorn -w 4 -b 0.0.0.0:5001 api:app &

# Start Web App
cd ../learningwebapp
gunicorn -w 4 -b 0.0.0.0:5000 app:app &
```

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run both services (use supervisor or separate containers in production)
CMD python ../learningtools/api.py & python app.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

[Add your license here]

## 📞 Support

For issues or questions:
- Check [Troubleshooting](#troubleshooting) section
- Review [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- Check terminal logs for errors

## 🎯 Roadmap

Future enhancements:
- [ ] WebSocket support for streaming output
- [ ] Code syntax highlighting (CodeMirror)
- [ ] Multi-language support (JavaScript, SQL)
- [ ] Collaborative editing
- [ ] Code execution history
- [ ] Download notebook functionality
- [ ] Docker sandboxing
- [ ] Admin dashboard
- [ ] Social features (leaderboards, etc.)

---

**Version**: 2.0.0 (API-based architecture)
**Last Updated**: May 2026
