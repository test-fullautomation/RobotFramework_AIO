# JupyterLab Integration Guide

## Overview

The Learning Tools Web Application now integrates with JupyterLab, allowing users to practice exercises in a full Jupyter notebook environment with automatic progress tracking.

## How It Works

### 1. Launch Workflow

```
Dashboard → Click "Start in Jupyter" → JupyterLab opens → Complete exercises → Return & Sync
```

### 2. Under the Hood

- **Notebook Setup**: When you click on a workbook, the system:
  - Creates a personal workspace for you (`user_workspaces/user_<id>/`)
  - Copies the template notebook from `learningtools/templates/`
  - Opens JupyterLab pointing to your notebook

- **Progress Tracking**: 
  - As you complete exercises using `p1.check()`, `p2.check()`, etc.
  - Progress is saved by the learningtools framework
  - When you return to the dashboard, progress syncs automatically

- **Isolation**:
  - Each user gets their own workspace
  - Notebooks are copied per-user to prevent conflicts
  - Changes you make don't affect other users

## Using JupyterLab

### Starting an Exercise

1. **Login** to the web application
2. **Go to Dashboard** - you'll see all available workbooks
3. **Click "Start in Jupyter →"** on any workbook
4. **Click "🚀 Open JupyterLab"** button
5. JupyterLab opens in a new tab

### Working in Jupyter

```python
# Example notebook cell workflow:

# 1. Run the setup cell (imports learningtools)
from learningtools import *
activate("RobotFrameworkAIO.Exercise_01")

# 2. Work on your solution
robot_code = """
*** Settings ***
Library    RobotFramework_TestsuitesManagement    WITH NAME    tm
Suite Setup    tm.testsuite_setup

*** Test Cases ***
My Test
    Log    Hello World    console=yes
"""

# 3. Check your answer
p1.check()  # Progress is automatically saved!

# 4. Get help if needed
# p1.hint()
# p1.solution()
```

### Returning to Dashboard

When done:
1. Click "Return to Dashboard" button (or navigate back)
2. Your progress will automatically sync
3. See your updated progress on the dashboard

### Manual Sync

You can manually sync at any time:
- Click "🔄 Sync Progress" button on the launch page
- Or navigate to "Return to Dashboard"

## Architecture

### Directory Structure

```
learningwebapp/
├── app.py                     # Main application with Jupyter integration
├── user_workspaces/           # Created automatically
│   ├── user_1/               # Personal workspace for user ID 1
│   │   ├── JsonPreprocessor_Comments/
│   │   │   └── Comments.ipynb
│   │   └── RobotFrameworkAIO_Exercise_01/
│   │       └── Exercise_01.ipynb
│   └── user_2/               # Personal workspace for user ID 2
│       └── ...
└── templates/
    ├── jupyter_launch.html    # Launch page
    └── ...
```

### Configuration

Key settings in `app.py`:

```python
app.config['JUPYTER_PORT'] = 8888          # JupyterLab port
app.config['JUPYTER_BASE_URL'] = '/jupyter'  # URL prefix
app.config['USER_WORKSPACES'] = Path('./user_workspaces')  # Workspace location
```

### JupyterLab Server

- Starts automatically when the app starts
- Runs on port 8888 by default
- No token/password (runs locally)
- Stops automatically when the app stops

## Troubleshooting

### JupyterLab Won't Start

**Problem**: "Failed to start JupyterLab"

**Solutions**:
1. Ensure JupyterLab is installed:
   ```bash
   pip install jupyterlab notebook
   ```

2. Check if port 8888 is available:
   ```bash
   netstat -an | findstr "8888"
   ```

3. Change the port in startup or set environment variable:
   ```bash
   set JUPYTER_PORT=8889
   python app.py
   ```

### Can't Access JupyterLab

**Problem**: JupyterLab URL doesn't work

**Solutions**:
1. Check that the webapp is still running
2. Ensure JupyterLab process is active
3. Try accessing directly: `http://localhost:8888/jupyter/lab`

### Progress Not Syncing

**Problem**: Completed exercises don't show as complete

**Solutions**:
1. Make sure you ran `p1.check()` or `p2.check()` in the notebook
2. Click "🔄 Sync Progress" manually
3. Check that the notebook is saving (look for checkpoint indicator)
4. Return to dashboard using the "Return to Dashboard" button

### Notebook Not Found

**Problem**: "Template notebook not found"

**Solutions**:
1. Ensure the template exists in `learningtools/templates/`
2. Check the workbook name matches the folder structure
3. Verify the template file ends with `_template.ipynb`

## Advanced Features

### Multiple Users

- Each user gets isolated workspace
- No interference between users
- Progress tracked independently

### Persistent Notebooks

- Your notebooks are saved between sessions
- Continue where you left off
- Changes persist until you delete the workspace

### Custom Configuration

Edit `app.py` to customize:

```python
# Change JupyterLab port
app.config['JUPYTER_PORT'] = 9999

# Change workspace location
app.config['USER_WORKSPACES'] = Path('/custom/path/workspaces')

# Change base URL
app.config['JUPYTER_BASE_URL'] = '/notebook'
```

## Security Considerations

### For Local Development

Current configuration (no token/password) is suitable for:
- Local machine only
- Single-user development
- Trusted network

### For Production/Multi-User

If deploying where multiple users access from different machines:

1. **Enable JupyterLab authentication**:
   ```python
   '--NotebookApp.token=<secure-token>',
   ```

2. **Use HTTPS**
3. **Firewall the JupyterLab port** (8888)
4. **Run behind reverse proxy**
5. **Implement user-specific Jupyter instances**

## FAQ

**Q: Can I use my own notebooks?**
A: Yes! Just place them in your user workspace folder.

**Q: What happens if I close the webapp?**
A: JupyterLab will stop, but your notebooks are saved.

**Q: Can I run multiple workbooks at once?**
A: Yes! Open each in a separate JupyterLab tab.

**Q: How do I reset my progress?**
A: Delete your workspace folder or specific notebook files.

**Q: Can I export my notebooks?**
A: Yes! Download them from JupyterLab (File → Download).

## Benefits of Jupyter Integration

✅ **Full IDE Experience** - Code completion, syntax highlighting, debugging  
✅ **Rich Output** - Images, plots, interactive widgets  
✅ **Real Environment** - Actual Python/Robot Framework execution  
✅ **Save Work** - Come back anytime, your code is saved  
✅ **Familiar Interface** - Standard Jupyter that many already know  
✅ **Auto Sync** - Progress automatically tracked  
✅ **Isolated** - Your workspace, your changes  

## Next Steps

1. Try launching your first notebook
2. Complete an exercise
3. Return and see your progress
4. Explore different workbooks
5. Share your experience!

---

**Happy Learning! 🎓📓**
