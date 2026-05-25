# Learning Tools API Documentation

## Overview

The Learning Tools platform now uses a **microservices architecture** with two main components:

1. **Learning Tools API** (Port 5001) - Python code execution engine
2. **Web Application** (Port 5000) - User interface and authentication

This architecture allows:
- ✅ **Browser-based code execution** - Users write and run code directly in the browser
- ✅ **Safe sandboxed execution** - Code runs on the server in isolated sessions
- ✅ **Real-time feedback** - Immediate output display and error messages
- ✅ **No JupyterLab required** - Simplified deployment and user experience
- ✅ **Session isolation** - Each user gets their own execution context

## Architecture

```
┌─────────────────┐         HTTP          ┌─────────────────┐
│                 │    POST /api/execute   │                 │
│   Web Browser   ├───────────────────────>│   Flask WebApp  │
│                 │<───────────────────────┤   (Port 5000)   │
└─────────────────┘         HTML           └────────┬────────┘
                                                    │
                                                    │ HTTP
                                                    │ Forward
                                                    │
                                           ┌────────▼────────┐
                                           │  Learning Tools │
                                           │      API        │
                                           │   (Port 5001)   │
                                           └────────┬────────┘
                                                    │
                                     ┌──────────────┼──────────────┐
                                     │              │              │
                              ┌──────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐
                              │  Session 1 │ │ Session 2 │ │ Session N │
                              │ (User 1)   │ │ (User 2)  │ │ (User N)  │
                              └────────────┘ └───────────┘ └───────────┘
```

## API Endpoints

### 1. Health Check
**GET** `/api/health`

Check if the API is running.

**Response:**
```json
{
  "status": "ok",
  "service": "learningtools-api"
}
```

---

### 2. List Workbooks
**GET** `/api/workbooks`

Get all available learning workbooks.

**Response:**
```json
{
  "workbooks": [
    {
      "name": "JsonPreprocessor.Comments",
      "title": "JSONP Comments",
      "summary": "Learn how to use comments in JSON",
      "question_count": 3
    }
  ]
}
```

---

### 3. Get Workbook Details
**GET** `/api/workbook/<workbook_name>`

Get detailed information about a specific workbook.

**Parameters:**
- `workbook_name` (path) - Workbook identifier (e.g., `JsonPreprocessor.Comments`)

**Response:**
```json
{
  "name": "JsonPreprocessor.Comments",
  "title": "JSONP Comments",
  "summary": "Learn how to use comments in JSON",
  "introduction": "In this lesson...",
  "questions": [
    {
      "question_id": "p1",
      "title": "Question 1",
      "prompt": "Parse JSON with comments",
      "hint_text": "Use syntax='python'",
      "solution_text": "json_object = CJsonPreprocessor(syntax='python')...",
      "starter_code": "# Your code here\n",
      "tags": ["jsonp", "comments"]
    }
  ]
}
```

---

### 4. Get Notebook Content
**GET** `/api/notebook/<workbook_name>`

Get the Jupyter notebook cells for browser display.

**Parameters:**
- `workbook_name` (path) - Workbook identifier

**Response:**
```json
{
  "workbook_name": "JsonPreprocessor.Comments",
  "cells": [
    {
      "cell_type": "markdown",
      "source": "# JSONP Comments\n\nLearn about comments...",
      "metadata": {}
    },
    {
      "cell_type": "code",
      "source": "from learningtools import *\nactivate('JsonPreprocessor.Comments')",
      "metadata": {}
    }
  ]
}
```

---

### 5. Execute Code
**POST** `/api/execute`

Execute Python code and return the output.

**Request Body:**
```json
{
  "code": "print('Hello, World!')",
  "workbook_name": "JsonPreprocessor.Comments",
  "session_id": "user_1"
}
```

**Response (Success):**
```json
{
  "success": true,
  "output": "Hello, World!\n",
  "error": null,
  "result": null
}
```

**Response (Error):**
```json
{
  "success": false,
  "output": "",
  "error": "NameError: name 'undefined_var' is not defined",
  "traceback": "Traceback (most recent call last):\n  File ..."
}
```

---

### 6. Create Session
**POST** `/api/session/create`

Create a new execution session for a user.

**Request Body:**
```json
{
  "workbook_name": "JsonPreprocessor.Comments",
  "session_id": "user_123"
}
```

**Response:**
```json
{
  "session_id": "user_123"
}
```

---

### 7. Reset Session
**POST** `/api/session/<session_id>/reset`

Reset a session's namespace (clear all variables).

**Parameters:**
- `session_id` (path) - Session identifier

**Response:**
```json
{
  "success": true
}
```

---

## How Code Execution Works

### 1. Session Management

Each user gets a unique **execution session** identified by `session_id`. The session maintains:
- **Namespace**: All defined variables, functions, and objects
- **Workbook context**: Which workbook is active
- **Execution history**: Previous code runs (in memory)

### 2. Safe Execution

Code is executed using Python's `exec()` in a controlled namespace:

```python
# Namespace includes:
- __builtins__      # Standard Python functions
- activate()        # Load learningtools workbook
- CJsonPreprocessor # JsonPreprocessor library
- os, sys, Path     # Common utilities
- json              # JSON module
```

### 3. Output Capture

All output (stdout, stderr) is captured and returned:
- `print()` statements → `output` field
- Return values → `result` field (if any)
- Errors → `error` and `traceback` fields

### 4. Learningtools Integration

When code calls `p1.check()`:
1. Validator runs in the session namespace
2. Output (hints, solutions, feedback) captured
3. Progress saved to learningtools.ProgressStore
4. All output returned to browser

---

## Web Application Integration

The web application (`app.py`) acts as a proxy:

1. **User clicks "Start Learning"** on dashboard
2. **Template notebook loaded** from `learningtools/templates/`
3. **Cells rendered** in browser with code editors
4. **User edits and runs code**
5. **Code sent to `/api/execute`** endpoint
6. **Output displayed** in browser
7. **Progress saved** to SQLite database

---

## Browser Interface

### Code Cell Features

- **Syntax highlighting** via monospace font
- **Run button** (Shift+Enter keyboard shortcut)
- **Reset button** to restore original code
- **Output panel** shows results/errors
- **Loading indicator** while executing
- **Error highlighting** for failures

### Markdown Cell Rendering

- Headers, bold, italic, code blocks
- Simple markdown parser
- Styled to match notebook appearance

---

## Installation & Setup

### 1. Install Dependencies

```bash
cd learningwebapp
pip install -r requirements.txt
```

**Requirements:**
- Flask==3.0.0
- Flask-Login==0.6.3
- Flask-CORS==4.0.0
- Werkzeug==3.0.1
- requests==2.31.0

### 2. Start the Platform

**Option A: Use the startup script (Windows)**
```cmd
start_with_api.bat
```

**Option B: Manual startup**

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

### 3. Access the Application

Open your browser to:
- **Web App**: http://localhost:5000
- **API**: http://localhost:5001 (for testing)

---

## Security Considerations

### Current Implementation (Development)

⚠️ **Warning**: The current implementation is for **development/educational use only**

**Security Risks:**
- Code execution uses `exec()` without sandboxing
- No resource limits (CPU, memory, time)
- No filesystem restrictions
- Users can import any module
- Sessions stored in memory (not persistent)

### Production Recommendations

For production use, implement:

1. **Sandboxed Execution**
   - Use Docker containers per session
   - Implement resource limits (CPU, memory, disk)
   - Restrict network access
   - Use `RestrictedPython` library

2. **Input Validation**
   - Validate code size limits
   - Check for dangerous imports
   - Rate limiting per user

3. **Session Management**
   - Use Redis for session storage
   - Implement session timeouts
   - Clean up old sessions

4. **Authentication**
   - HTTPS only
   - Secure session cookies
   - CSRF protection
   - Rate limiting

**Example Docker Sandboxing:**
```python
import docker

client = docker.from_env()
container = client.containers.run(
    'python:3.9-slim',
    f'python -c "{code}"',
    mem_limit='256m',
    cpu_period=100000,
    cpu_quota=50000,  # 50% of one CPU
    network_disabled=True,
    detach=True
)
```

---

## Testing the API

### Using curl

**Health Check:**
```bash
curl http://localhost:5001/api/health
```

**List Workbooks:**
```bash
curl http://localhost:5001/api/workbooks
```

**Execute Code:**
```bash
curl -X POST http://localhost:5001/api/execute \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(2 + 2)",
    "workbook_name": "test",
    "session_id": "test_session"
  }'
```

### Using Python

```python
import requests

# Execute code
response = requests.post('http://localhost:5001/api/execute', json={
    'code': 'x = 10\nprint(x * 2)',
    'workbook_name': 'test',
    'session_id': 'my_session'
})

result = response.json()
print(result['output'])  # "20"
```

---

## Troubleshooting

### API Not Starting

**Error**: `Address already in use`

**Solution**: Another process is using port 5001
```bash
# Windows
netstat -ano | findstr :5001
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :5001
kill -9 <PID>
```

### Code Execution Timeout

**Error**: `Request timeout`

**Solution**: Increase timeout in `app.py`:
```python
response = requests.post(api_url, json=data, timeout=60)  # 60 seconds
```

### Module Not Found

**Error**: `ModuleNotFoundError: No module named 'CJsonPreprocessor'`

**Solution**: Add module to API `setup_namespace()`:
```python
from module_name import ClassName
self.namespace['ClassName'] = ClassName
```

### CORS Issues

If running webapp on different port:

1. Update `CORS(app)` in `api.py`
2. Or specify origins:
```python
from flask_cors import CORS
CORS(app, origins=['http://localhost:5000'])
```

---

## Development Tips

### Adding New Workbooks

1. Create `.jsonp` and `.py` files in `learningtools/workbooks/`
2. Create `_template.ipynb` in `learningtools/templates/`
3. Restart API server
4. Workbook appears automatically in dashboard

### Debugging Code Execution

Add logging to `api.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

def execute(self, code):
    logging.debug(f"Executing code: {code[:100]}")
    # ... rest of code
```

### Custom Validators

Add to `learningtools/runtime.py`:
```python
def my_custom_validator(actual, expected):
    return actual == expected
```

Then use in workbook:
```python
p1 = Question(
    'p1',
    validator=my_custom_validator,
    expected=42
)
```

---

## Future Enhancements

Planned improvements:
- [ ] WebSocket support for real-time output streaming
- [ ] Code autocomplete in browser
- [ ] Syntax highlighting with CodeMirror
- [ ] Multiple language support (JavaScript, SQL, etc.)
- [ ] Collaborative editing (multiple users)
- [ ] Code execution history
- [ ] Download results as notebook
- [ ] Docker-based sandboxing
- [ ] Resource usage monitoring
- [ ] Admin dashboard for monitoring sessions

---

## Migration from JupyterLab

The old JupyterLab integration has been preserved in `app_old_jupyter.py`.

**Key Differences:**

| Feature | JupyterLab | API-based |
|---------|-----------|-----------|
| Execution | Client-side in Jupyter | Server-side via API |
| User Experience | Full Jupyter environment | Simplified browser UI |
| Setup | Requires JupyterLab install | Just Flask + requests |
| Scalability | One Jupyter per user | Shared API, lightweight sessions |
| Deployment | Complex (JupyterHub) | Simple (2 Flask apps) |
| Customization | Limited | Full control |

**Advantages of API approach:**
- ✅ Easier deployment
- ✅ Better control over UI/UX
- ✅ Simpler maintenance
- ✅ Lower resource usage
- ✅ Integrated with webapp seamlessly

---

## API Reference Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Health check |
| `/api/workbooks` | GET | List all workbooks |
| `/api/workbook/<name>` | GET | Get workbook details |
| `/api/notebook/<name>` | GET | Get notebook cells |
| `/api/execute` | POST | Execute code |
| `/api/session/create` | POST | Create session |
| `/api/session/<id>/reset` | POST | Reset session |

---

## Support

For issues or questions:
1. Check logs in terminal windows
2. Review [Troubleshooting](#troubleshooting) section
3. Check Flask debug output for errors
4. Test API directly with curl/Postman

---

**Version**: 2.0.0 (API-based architecture)
**Last Updated**: May 2026
