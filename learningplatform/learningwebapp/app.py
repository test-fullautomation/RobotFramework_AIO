"""
Learning Tools Web Application
Provides a web interface for learningtools exercises with user authentication and progress tracking.
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import sys
from pathlib import Path
from datetime import datetime
import json
import requests
import markdown
import html

# Add learningtools to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from learningtools.loader import load_workbook_definition
from learningtools.storage import ProgressStore
from typing import List

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'webapp.db')
app.config['API_BASE_URL'] = os.environ.get('API_BASE_URL', 'http://localhost:5001')

# Disable proxies for localhost connections (important for servers with proxy settings)
REQUESTS_NO_PROXY = {
    'http': None,
    'https': None,
    'no_proxy': 'localhost,127.0.0.1,::1'
}

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# Database Helper Functions
def get_db():
    """Get database connection with better concurrency support."""
    db = sqlite3.connect(
        app.config['DATABASE'],
        timeout=30.0,  # Wait up to 30 seconds if database is locked
        isolation_level=None,  # Autocommit mode
        check_same_thread=False  # Allow sharing connection across threads
    )
    db.row_factory = sqlite3.Row
    # Enable Write-Ahead Logging for better concurrency
    db.execute('PRAGMA journal_mode=WAL')
    db.execute('PRAGMA busy_timeout=30000')  # 30 seconds in milliseconds
    return db


def init_db():
    """Initialize the database."""
    db = None
    try:
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS user_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                workbook_name TEXT NOT NULL,
                question_id TEXT NOT NULL,
                completed BOOLEAN DEFAULT 0,
                completed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, workbook_name, question_id)
            )
        ''')
        # No explicit commit needed with autocommit mode
    finally:
        if db:
            db.close()


# User Model
class User(UserMixin):
    def __init__(self, id, username, email=None):
        self.id = id
        self.username = username
        self.email = email


@login_manager.user_loader
def load_user(user_id):
    db = None
    try:
        db = get_db()
        user_row = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        if user_row:
            return User(user_row['id'], user_row['username'], user_row['email'])
        return None
    finally:
        if db:
            db.close()


# Helper Functions
def discover_all_workbooks(package_dir: Path):
    """Discover all workbooks including nested ones."""
    workbooks_root = package_dir / "workbooks"
    if not workbooks_root.exists():
        return []
    
    workbooks = []
    for jsonp_path in workbooks_root.rglob("*.jsonp"):
        if jsonp_path.name.startswith("_"):
            continue
        rel_path = jsonp_path.relative_to(workbooks_root)
        workbook_name = str(rel_path.with_suffix("")).replace("\\", ".").replace("/", ".")
        py_path = workbooks_root / str(rel_path.with_suffix(".py"))
        if py_path.exists():
            workbooks.append(workbook_name)
    
    return sorted(workbooks)


def get_user_progress(user_id, workbook_name):
    """Get user's progress for a workbook."""
    db = None
    try:
        db = get_db()
        completed = db.execute('''
            SELECT question_id FROM user_progress 
            WHERE user_id = ? AND workbook_name = ? AND completed = 1
        ''', (user_id, workbook_name)).fetchall()
        return [row['question_id'] for row in completed]
    finally:
        if db:
            db.close()


def update_progress(user_id, workbook_name, question_id, completed=True):
    """Update user's progress with retry on lock errors."""
    import time
    max_retries = 5
    retry_delay = 0.05  # Start with 50ms
    
    for attempt in range(max_retries):
        db = None
        try:
            db = get_db()
            # Check if already completed to avoid unnecessary writes
            existing = db.execute('''
                SELECT completed FROM user_progress 
                WHERE user_id = ? AND workbook_name = ? AND question_id = ?
            ''', (user_id, workbook_name, question_id)).fetchone()
            
            if existing and existing['completed'] == 1 and completed:
                # Already completed, skip update
                return
            
            db.execute('''
                INSERT OR REPLACE INTO user_progress (user_id, workbook_name, question_id, completed, completed_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, workbook_name, question_id, completed, datetime.now() if completed else None))
            # No explicit commit needed with autocommit mode
            return  # Success
        except sqlite3.OperationalError as e:
            if 'locked' in str(e).lower() and attempt < max_retries - 1:
                time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                continue
            else:
                # Log error but don't crash - progress sync is non-critical
                print(f"Warning: Failed to update progress after {max_retries} attempts: {e}")
                return
        except Exception as e:
            print(f"Error updating progress: {e}")
            return
        finally:
            if db:
                db.close()


def get_user_workspace_path(user_id, workbook_name):
    """Get or create user workspace directory for a workbook."""
    # Create user workspace structure: user_workspaces/user_<id>/<workbook_name>/
    workspace_root = Path(__file__).parent / 'user_workspaces' / f'user_{user_id}' / workbook_name.replace('.', '_')
    workspace_root.mkdir(parents=True, exist_ok=True)
    return str(workspace_root.absolute())


# Routes
@app.route('/')
def index():
    """Home page."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('register.html')
        
        db = None
        try:
            db = get_db()
            # Check if user already exists
            existing_user = db.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
            if existing_user:
                flash('Username already exists', 'error')
                return render_template('register.html')
            
            # Create new user
            password_hash = generate_password_hash(password)
            db.execute('INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)',
                       (username, password_hash, email))
            # No explicit commit needed with autocommit mode
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.Error as e:
            flash(f'Registration failed: {str(e)}', 'error')
            return render_template('register.html')
        finally:
            if db:
                db.close()
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        db = None
        try:
            db = get_db()
            user_row = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            
            if user_row and check_password_hash(user_row['password_hash'], password):
                user = User(user_row['id'], user_row['username'], user_row['email'])
                login_user(user)
                
                # Create session for code execution
                session['execution_session_id'] = f"user_{user.id}"
                
                next_page = request.args.get('next')
                return redirect(next_page or url_for('dashboard'))
            else:
                flash('Invalid username or password', 'error')
        finally:
            if db:
                db.close()
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing all workbook categories."""
    learningtools_dir = BASE_DIR / 'learningtools'
    workbooks = discover_all_workbooks(learningtools_dir)
    
    # Note: Progress is synced during code execution, not here
    # This avoids incorrectly syncing other users' progress
    
    # Group workbooks by category (first part before the dot)
    categories = {}
    for wb_name in workbooks:
        try:
            wb_def = load_workbook_definition(learningtools_dir, wb_name)
            completed = get_user_progress(current_user.id, wb_name)
            total_questions = len(wb_def.questions)
            progress = int((len(completed) / total_questions * 100)) if total_questions > 0 else 0
            
            # Extract category (e.g., "JsonPreprocessor" from "JsonPreprocessor.Comments")
            if '.' in wb_name:
                category = wb_name.split('.')[0]
            else:
                category = 'General'
            
            if category not in categories:
                categories[category] = {
                    'name': category,
                    'workbooks': [],
                    'total_exercises': 0,
                    'completed_exercises': 0
                }
            
            categories[category]['workbooks'].append({
                'name': wb_name,
                'title': wb_def.title,
                'summary': wb_def.summary,
                'total_questions': total_questions,
                'completed_questions': len(completed),
                'progress': progress
            })
            categories[category]['total_exercises'] += total_questions
            categories[category]['completed_exercises'] += len(completed)
            
        except Exception as e:
            continue
    
    # Calculate overall progress for each category
    for category_data in categories.values():
        if category_data['total_exercises'] > 0:
            category_data['progress'] = int(
                (category_data['completed_exercises'] / category_data['total_exercises'] * 100)
            )
        else:
            category_data['progress'] = 0
    
    return render_template('dashboard.html', categories=categories)


@app.route('/category/<category_name>')
@login_required
def category(category_name):
    """Display exercises within a specific category."""
    learningtools_dir = BASE_DIR / 'learningtools'
    workbooks = discover_all_workbooks(learningtools_dir)
    
    # Note: Progress is synced during code execution, not here
    # This avoids incorrectly syncing other users' progress
    
    # Build category workbooks list
    category_workbooks = []
    for wb_name in workbooks:
        if '.' in wb_name:
            wb_category = wb_name.split('.')[0]
        else:
            wb_category = 'General'
        
        if wb_category == category_name:
            try:
                wb_def = load_workbook_definition(learningtools_dir, wb_name)
                completed = get_user_progress(current_user.id, wb_name)
                total_questions = len(wb_def.questions)
                progress = int((len(completed) / total_questions * 100)) if total_questions > 0 else 0
                
                category_workbooks.append({
                    'name': wb_name,
                    'title': wb_def.title,
                    'summary': wb_def.summary,
                    'total_questions': total_questions,
                    'completed_questions': len(completed),
                    'progress': progress
                })
            except Exception as e:
                continue
    
    if not category_workbooks:
        flash(f'No exercises found in category: {category_name}', 'warning')
        return redirect(url_for('dashboard'))
    
    return render_template('category.html', category_name=category_name, workbooks=category_workbooks)


@app.route('/workbook/<path:workbook_name>')
@login_required
def workbook(workbook_name):
    """Display workbook exercises in browser."""
    try:
        # Get notebook content from API
        api_url = f"{app.config['API_BASE_URL']}/api/notebook/{workbook_name}"
        response = requests.get(api_url, timeout=5, proxies=REQUESTS_NO_PROXY)
        
        if response.status_code != 200:
            flash('Could not load workbook. Make sure the API is running.', 'error')
            return redirect(url_for('dashboard'))
        
        notebook_data = response.json()
        
        # Convert markdown cells to HTML
        for cell in notebook_data['cells']:
            if cell.get('cell_type') == 'markdown':
                markdown_text = cell.get('source', '')
                # Convert markdown to HTML with extensions
                html_content = markdown.markdown(
                    markdown_text,
                    extensions=['fenced_code', 'tables', 'nl2br', 'sane_lists']
                )
                cell['html_content'] = html_content
            elif cell.get('cell_type') == 'code':
                # For RobotFrameworkAIO exercises, extract robot scripts and check() calls
                if workbook_name.startswith("RobotFrameworkAIO"):
                    source = cell.get('source', '')
                    
                    # Pattern 1: robot_code = """...""" followed by pX.check()
                    if 'robot_code = """' in source or "robot_code = f\"\"\"" in source:
                        # Determine if it's f-string or not
                        is_fstring = "robot_code = f\"\"\"" in source
                        
                        # Extract the robot script content
                        start_marker = 'robot_code = f"""' if is_fstring else 'robot_code = """'
                        start_idx = source.find(start_marker)
                        if start_idx != -1:
                            content_start = start_idx + len(start_marker)
                            # Find the closing """
                            end_idx = source.find('"""', content_start)
                            if end_idx != -1:
                                robot_script = source[content_start:end_idx].strip()
                                
                                # Store the display version (just the script)
                                cell['display_source'] = robot_script
                                
                                # Create execution template
                                if is_fstring:
                                    cell['execution_template'] = "robot_code = f'''{USER_CODE}'''\n" + source[end_idx + 3:].strip()
                                else:
                                    cell['execution_template'] = "robot_code = '''{USER_CODE}'''\n" + source[end_idx + 3:].strip()
                    
                    # Pattern 2: json_config = """...""" with file writing
                    elif 'json_config = """' in source and 'config_file_path' in source:
                        # Extract just the JSON content
                        start_marker = 'json_config = """'
                        start_idx = source.find(start_marker)
                        if start_idx != -1:
                            content_start = start_idx + len(start_marker)
                            end_idx = source.find('"""', content_start)
                            if end_idx != -1:
                                json_content = source[content_start:end_idx].strip()
                                
                                # Store display version (just JSON)
                                cell['display_source'] = json_content
                                
                                # Create execution template with the rest of the code
                                cell['execution_template'] = "json_config = '''{USER_CODE}'''\n" + source[end_idx + 3:].strip()
        
        # Get workbook details
        learningtools_dir = BASE_DIR / 'learningtools'
        wb_def = load_workbook_definition(learningtools_dir, workbook_name)
        
        # Get user progress from database
        # Note: Progress is synced during code execution via the execute API response
        completed = get_user_progress(current_user.id, workbook_name)
        
        # Create user workspace for this workbook
        user_workspace_path = get_user_workspace_path(current_user.id, workbook_name)
        
        # Create session for this workbook
        session_id = session.get('execution_session_id', f"user_{current_user.id}")
        try:
            requests.post(
                f"{app.config['API_BASE_URL']}/api/session/create",
                json={
                    'workbook_name': workbook_name, 
                    'session_id': session_id,
                    'user_id': current_user.id,
                    'user_workspace_path': user_workspace_path
                },
                timeout=5,
                proxies=REQUESTS_NO_PROXY
            )
        except:
            pass  # Session might already exist
        
        # Auto-execute the first code cell (initialization)
        first_cell_output = None
        first_code_cell_index = None
        
        # Find the first code cell
        for idx, cell in enumerate(notebook_data['cells']):
            if cell.get('cell_type') == 'code':
                first_code_cell_index = idx
                first_code = cell.get('source', '')
                try:
                    api_url = f"{app.config['API_BASE_URL']}/api/execute"
                    exec_response = requests.post(api_url, json={
                        'code': first_code,
                        'workbook_name': workbook_name,
                        'session_id': session_id
                    }, timeout=30, proxies=REQUESTS_NO_PROXY)
                    
                    if exec_response.status_code == 200:
                        first_cell_output = exec_response.json()
                        
                        # Sync any progress updates from the initialization cell
                        if 'completed_questions' in first_cell_output:
                            for question_id in first_cell_output.get('completed_questions', []):
                                try:
                                    update_progress(current_user.id, workbook_name, question_id, True)
                                except:
                                    pass
                        
                        # Convert output to markdown HTML
                        if first_cell_output.get('success') and first_cell_output.get('output'):
                            output_text = first_cell_output['output']
                            first_cell_output['output_html'] = markdown.markdown(
                                output_text,
                                extensions=['fenced_code', 'tables', 'nl2br', 'sane_lists']
                            )
                    else:
                        first_cell_output = {
                            'success': False,
                            'error': f'API returned status {exec_response.status_code}',
                            'output': ''
                        }
                except Exception as e:
                    first_cell_output = {
                        'success': False,
                        'error': f'Failed to initialize: {str(e)}',
                        'output': ''
                    }
                break  # Only execute the first code cell
        
        return render_template('workbook_execute.html',
                             workbook=wb_def,
                             cells=notebook_data['cells'],
                             completed=completed,
                             session_id=session_id,
                             first_cell_output=first_cell_output,
                             first_code_cell_index=first_code_cell_index)
    
    except Exception as e:
        flash(f'Error loading workbook: {str(e)}', 'error')
        return redirect(url_for('dashboard'))


@app.route('/api/execute', methods=['POST'])
@login_required
def execute_code():
    """Execute code via API and return results."""
    try:
        data = request.get_json()
        code = data.get('code', '')
        workbook_name = data.get('workbook_name', '')
        session_id = session.get('execution_session_id', f"user_{current_user.id}")
        
        # Forward to learningtools API
        api_url = f"{app.config['API_BASE_URL']}/api/execute"
        response = requests.post(api_url, json={
            'code': code,
            'workbook_name': workbook_name,
            'session_id': session_id
        }, timeout=30, proxies=REQUESTS_NO_PROXY)
        
        result = response.json()
        
        # Sync progress to database if execution was successful
        if response.status_code == 200 and 'completed_questions' in result:
            completed_questions = result.get('completed_questions', [])
            for question_id in completed_questions:
                try:
                    update_progress(current_user.id, workbook_name, question_id, True)
                except Exception as sync_error:
                    # Log but don't fail the request if progress sync fails
                    print(f"Warning: Failed to sync progress for {question_id}: {sync_error}")
        
        return jsonify(result), response.status_code
    
    except requests.Timeout:
        return jsonify({'success': False, 'error': 'Execution timeout'}), 504
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/progress/<path:workbook_name>/<question_id>', methods=['POST'])
@login_required
def mark_complete(workbook_name, question_id):
    """Mark a question as complete."""
    try:
        update_progress(current_user.id, workbook_name, question_id, True)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/progress/sync/<path:workbook_name>', methods=['POST'])
@login_required
def sync_progress(workbook_name):
    """Sync progress from learningtools API ProgressStore to webapp database."""
    try:
        # Get progress from learningtools API
        api_url = f"{app.config['API_BASE_URL']}/api/progress/{workbook_name}"
        response = requests.get(api_url, timeout=5, proxies=REQUESTS_NO_PROXY)
        
        if response.status_code != 200:
            return jsonify({'success': False, 'error': 'Failed to retrieve progress from API'}), 500
        
        progress_data = response.json()
        completed_questions = progress_data.get('completed_questions', [])
        
        # Update database with completed questions
        synced_count = 0
        for question_id in completed_questions:
            try:
                update_progress(current_user.id, workbook_name, question_id, True)
                synced_count += 1
            except Exception as sync_error:
                print(f"Warning: Failed to sync {question_id}: {sync_error}")
        
        return jsonify({
            'success': True,
            'synced_count': synced_count,
            'completed_questions': completed_questions
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize database
    if not os.path.exists(app.config['DATABASE']):
        init_db()
    
    print('=' * 60)
    print('Starting Learning Tools Web Application...')
    print('Web app will be available at: http://0.0.0.0:5000')
    print('Make sure the API is running at:', app.config['API_BASE_URL'])
    print('=' * 60)
    
    # Use debug=False in production, True only for development
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    try:
        app.run(debug=debug_mode, host='0.0.0.0', port=5000, threaded=True)
    except Exception as e:
        print(f'ERROR: Failed to start web application: {e}')
        import traceback
        traceback.print_exc()
