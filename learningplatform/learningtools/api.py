"""
Learning Tools API
Provides API endpoints for executing learningtools exercises and tracking progress.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import io
import os
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr
import traceback
import json

# Bypass proxy for localhost and internal connections
os.environ['NO_PROXY'] = 'localhost,127.0.0.1,::1'
os.environ['no_proxy'] = 'localhost,127.0.0.1,::1'

# Disable Jupyter notebook detection (we're using API mode)
os.environ['LEARNINGTOOLS_DISABLE_JUPYTER_DETECTION'] = '1'

# Add learningtools to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from learningtools.loader import load_workbook_definition
from learningtools.runtime import Question, Lesson
from learningtools.capture import get_output_capture
from learningtools.storage import ProgressStore

app = Flask(__name__)
CORS(app)  # Enable CORS for webapp communication

# Store active sessions (in production, use Redis)
active_sessions = {}


class CodeExecutor:
    """Safely execute user code with learningtools context."""
    
    def __init__(self, workbook_name, user_id=None, user_workspace_path=None):
        self.workbook_name = workbook_name
        self.user_id = user_id
        self.user_workspace_path = user_workspace_path
        
        # Set user-specific progress directory BEFORE importing learningtools
        # This ensures each user has their own progress file
        if user_id and user_workspace_path:
            # Store progress in user's workspace directory
            progress_dir = Path(user_workspace_path).parent / '.progress'
            progress_dir.mkdir(parents=True, exist_ok=True)
            os.environ['LEARNINGTOOLS_PROGRESS_DIR'] = str(progress_dir)
        
        self.namespace = {}
        self.setup_namespace()
    
    def setup_namespace(self):
        """Initialize namespace with learningtools."""
        # Import learningtools components
        sys.path.insert(0, str(BASE_DIR))
        
        # Add learningtools to namespace
        import learningtools
        from learningtools import activate
        
        self.namespace['__builtins__'] = __builtins__
        self.namespace['activate'] = activate
        self.namespace['learningtools'] = learningtools
        
        # Add common imports
        self.namespace['os'] = __import__('os')
        self.namespace['sys'] = sys
        self.namespace['Path'] = Path
        self.namespace['json'] = json
        
        # Add JsonPreprocessor if available
        try:
            from JsonPreprocessor.CJsonPreprocessor import CJsonPreprocessor
            self.namespace['CJsonPreprocessor'] = CJsonPreprocessor
        except ImportError:
            pass
        
        # Add user workspace information
        if self.user_workspace_path:
            self.namespace['USER_WORKSPACE'] = self.user_workspace_path
            self.namespace['USER_ID'] = self.user_id
        else:
            # Fallback for non-webapp usage
            self.namespace['USER_WORKSPACE'] = str(BASE_DIR / 'learningtools' / 'examples')
            self.namespace['USER_ID'] = 'default'
    
    def execute(self, code):
        """Execute code and capture output."""
        # Ensure user-specific progress directory is set for this execution
        if self.user_id and self.user_workspace_path:
            progress_dir = Path(self.user_workspace_path).parent / '.progress'
            progress_dir.mkdir(parents=True, exist_ok=True)
            os.environ['LEARNINGTOOLS_PROGRESS_DIR'] = str(progress_dir)
        
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        result = {
            'success': False,
            'output': '',
            'error': None,
            'result': None
        }
        
        try:
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                # Execute the code
                exec(code, self.namespace)
                
                # After execution, check if activate() was called and update namespace
                # with question objects (p1, p2, etc.)
                if 'learningtools' in self.namespace:
                    from learningtools.core import current_lesson
                    lesson = current_lesson()
                    if lesson is not None:
                        # Add lesson object
                        self.namespace['lesson'] = lesson
                        # Add all question objects (p1, p2, p3, etc.)
                        for question_id, question_obj in lesson.questions.items():
                            self.namespace[question_id] = question_obj
            
            result['success'] = True
            result['output'] = stdout_capture.getvalue()
            
            # Capture any stderr
            stderr_output = stderr_capture.getvalue()
            if stderr_output:
                result['output'] += '\n' + stderr_output
                
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
            result['output'] = stderr_capture.getvalue()
            result['traceback'] = traceback.format_exc()
        
        return result


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'service': 'learningtools-api'})


@app.route('/api/workbooks', methods=['GET'])
def list_workbooks():
    """List all available workbooks."""
    try:
        from learningtools.loader import load_workbook_definition
        learningtools_dir = BASE_DIR / 'learningtools'
        
        # Discover workbooks
        workbooks = discover_all_workbooks(learningtools_dir)
        
        workbooks_data = []
        for wb_name in workbooks:
            try:
                wb_def = load_workbook_definition(learningtools_dir, wb_name)
                workbooks_data.append({
                    'name': wb_def.name,
                    'title': wb_def.title,
                    'summary': wb_def.summary,
                    'question_count': len(wb_def.questions)
                })
            except Exception:
                continue
        
        return jsonify({'workbooks': workbooks_data})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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


@app.route('/api/workbook/<path:workbook_name>', methods=['GET'])
def get_workbook(workbook_name):
    """Get workbook details and questions."""
    try:
        learningtools_dir = BASE_DIR / 'learningtools'
        wb_def = load_workbook_definition(learningtools_dir, workbook_name)
        
        questions_data = []
        for q_id, q_def in wb_def.questions.items():
            questions_data.append({
                'question_id': q_def.question_id,
                'title': q_def.title,
                'prompt': q_def.prompt,
                'hint_text': q_def.hint_text,
                'solution_text': q_def.solution_text,
                'starter_code': q_def.starter_code,
                'tags': q_def.tags
            })
        
        return jsonify({
            'name': wb_def.name,
            'title': wb_def.title,
            'summary': wb_def.summary,
            'introduction': wb_def.introduction,
            'questions': questions_data
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/notebook/<path:workbook_name>', methods=['GET'])
def get_notebook_content(workbook_name):
    """Get notebook cells content for display."""
    try:
        learningtools_dir = BASE_DIR / 'learningtools'
        template_path = learningtools_dir / 'templates' / f"{workbook_name.replace('.', '/')}_template.ipynb"
        
        if not template_path.exists():
            return jsonify({'error': 'Notebook template not found'}), 404
        
        with open(template_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        cells = []
        for cell in notebook.get('cells', []):
            cells.append({
                'cell_type': cell.get('cell_type'),
                'source': ''.join(cell.get('source', [])),
                'metadata': cell.get('metadata', {})
            })
        
        return jsonify({'cells': cells, 'workbook_name': workbook_name})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/execute', methods=['POST'])
def execute_code():
    """Execute user code and return output."""
    try:
        data = request.get_json()
        code = data.get('code', '')
        workbook_name = data.get('workbook_name', '')
        session_id = data.get('session_id', 'default')
        
        if not code:
            return jsonify({'error': 'No code provided'}), 400
        
        # Get or create executor for session
        if session_id not in active_sessions:
            active_sessions[session_id] = CodeExecutor(workbook_name)
        
        executor = active_sessions[session_id]
        result = executor.execute(code)
        
        # Get current progress from ProgressStore after execution
        from learningtools.core import get_progress
        progress = get_progress(workbook_name)
        completed_questions = [qid for qid, details in progress.items() if details.get('completed')]
        result['completed_questions'] = completed_questions
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/check/<path:workbook_name>/<question_id>', methods=['POST'])
def check_answer(workbook_name, question_id):
    """Check an answer using learningtools validators."""
    try:
        data = request.get_json()
        session_id = data.get('session_id', 'default')
        
        # Get executor session
        if session_id not in active_sessions:
            return jsonify({'error': 'No active session'}), 400
        
        executor = active_sessions[session_id]
        
        # The check should have been called in the executed code
        # Here we just return success (the actual check happened during execution)
        return jsonify({
            'success': True,
            'message': 'Answer checked'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/session/create', methods=['POST'])
def create_session():
    """Create a new execution session."""
    try:
        data = request.get_json()
        workbook_name = data.get('workbook_name', '')
        session_id = data.get('session_id') or f"session_{len(active_sessions)}"
        user_id = data.get('user_id')
        user_workspace_path = data.get('user_workspace_path')
        
        active_sessions[session_id] = CodeExecutor(workbook_name, user_id, user_workspace_path)
        
        return jsonify({'session_id': session_id})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/session/<session_id>/reset', methods=['POST'])
def reset_session(session_id):
    """Reset an execution session."""
    try:
        if session_id in active_sessions:
            old_executor = active_sessions[session_id]
            workbook_name = old_executor.workbook_name
            user_id = old_executor.user_id
            user_workspace_path = old_executor.user_workspace_path
            active_sessions[session_id] = CodeExecutor(workbook_name, user_id, user_workspace_path)
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/progress/<path:workbook_name>', methods=['GET'])
def get_workbook_progress(workbook_name):
    """Get progress for a specific workbook from ProgressStore."""
    try:
        from learningtools.core import get_progress
        progress = get_progress(workbook_name)
        
        # Extract completed question IDs
        completed_questions = [
            qid for qid, details in progress.items() 
            if isinstance(details, dict) and details.get('completed')
        ]
        
        return jsonify({
            'workbook_name': workbook_name,
            'completed_questions': completed_questions,
            'progress': progress
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print('=' * 60)
    print('Starting Learning Tools API...')
    print('API will be available at: http://0.0.0.0:5001')
    print('Health check: http://localhost:5001/api/health')
    print('=' * 60)
    
    # Use debug=False in production, True only for development
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    try:
        app.run(debug=debug_mode, host='0.0.0.0', port=5001, threaded=True)
    except Exception as e:
        print(f'ERROR: Failed to start API server: {e}')
        import traceback
        traceback.print_exc()
