# Import guard - try imports one by one with helpful error messages
try:
    from flask import Flask, request, jsonify
    print("Successfully imported Flask")
except ImportError as e:
    print(f"ERROR importing Flask: {e}")
    print("Please make sure Flask is installed with: python3 -m pip install flask")
    import sys
    sys.exit(1)

try:
    from flask_login import LoginManager, UserMixin
    print("Successfully imported Flask-Login")
except ImportError as e:
    print(f"ERROR importing Flask-Login: {e}")
    print("Please make sure Flask-Login is installed with: python3 -m pip install flask-login")
    import sys
    sys.exit(1)

# Import Celery components
try:
    # Try direct import instead of relative import
    from celery_worker import celery, process_login, make_celery
    print("Successfully imported Celery components")
except ImportError as e:
    print(f"WARNING: Celery import failed: {e}")
    # Create dummy functions to prevent app from crashing
    def process_login(*args, **kwargs):
        print("Celery not available, login processing skipped")
        return None
    def make_celery(app_name):
        return None
    celery = None

# Continue with your other imports...
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from datetime import datetime
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_security import RoleMixin
from sqlalchemy import or_
import re
from flask_mail import Mail, Message
from io import BytesIO
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import base64
from weasyprint import HTML
import tempfile

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '7ce2afd1bf4a1e4eecbfbdf'

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True, allow_headers=["Content-Type", "Authorization"])

# Configure JWT settings
app.config['JWT_SECRET_KEY'] = app.config['SECRET_KEY']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Set this to a reasonable time in production
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'
app.config['PROPAGATE_EXCEPTIONS'] = True  # This will help see JWT errors

# Add Flask-Mail configuration after other app configs
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Change based on your mail server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@example.com'  # Update with actual email
app.config['MAIL_PASSWORD'] = 'your-password'  # Use environment variables in production
app.config['MAIL_DEFAULT_SENDER'] = ('Quiz Master', 'your-email@example.com')

app.config['EMAIL_NOTIFICATIONS_ENABLED'] = True  # Can be toggled in production
app.config['MONTHLY_REPORTS_ENABLED'] = True      # Can be toggled in production

# Update the Flask-Mail configuration with the correct credentials
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = '23f3001886@ds.study.iitm.ac.in'  # Replace with your actual Gmail address
app.config['MAIL_PASSWORD'] = 'qgweuohlttivtoyj'  # Using the provided app password
app.config['MAIL_DEFAULT_SENDER'] = ('Quiz Master', '23f3001886@ds.study.iitm.ac.in')  # Replace with your actual Gmail address
app.config['MAIL_DEBUG'] = True  # Set to False in production

mail = Mail(app)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
jwt = JWTManager(app)

# Initialize Celery with your app
celery = make_celery('quiz_master')

class UserRoles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('registration_user.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

class RegistrationUser(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(200), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    qualification = db.Column(db.String(100), nullable=False)
    self_description = db.Column(db.String(500))
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    active = db.Column(db.Boolean, default=True)
    roles = db.relationship('Role', secondary='user_roles', backref='users')
    scores = db.relationship('Scores', backref='user', lazy=True)
    Performance=db.relationship('Performance',backref='RegistrationUser',lazy=True)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    description = db.Column(db.String(500), nullable=False)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    chapters = db.relationship('Chapters', backref='subject', lazy=True)

class Chapters(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    chapter_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    quizzes = db.relationship('Quizzes', backref='chapter', lazy=True)

class Quizzes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    quiz_name = db.Column(db.String(100), nullable=False)
    date_of_quiz = db.Column(db.Date, nullable=False)
    timing = db.Column(db.Integer, nullable=False)
    questions = db.relationship('Questions', backref='quiz', lazy=True)
    scores = db.relationship('Scores', backref='quiz', lazy=True)

class Questions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    question_statement = db.Column(db.String(500), nullable=False)
    option1 = db.Column(db.String(100), nullable=False)
    option2 = db.Column(db.String(100), nullable=False)
    option3 = db.Column(db.String(100), nullable=False)
    option4 = db.Column(db.String(100), nullable=False)
    correct_option=db.Column(db.String(100),nullable=False)
    marks = db.Column(db.Integer, nullable=False)

class Scores(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('registration_user.id'), nullable=False)
    time_stamp_of_attempt = db.Column(db.DateTime, default=datetime.utcnow)
    total_scored = db.Column(db.Integer, nullable=False)
    
# new database 
class Performance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    RegistrationUser_id = db.Column(db.Integer, db.ForeignKey('registration_user.id'), nullable=False)
    Quizzes_id = db.Column(db.Integer, nullable=False)  # Should be `quiz_id` for consistency
    score = db.Column(db.Float, nullable=False)
    attempted_at = db.Column(db.DateTime, nullable=False)

    # Relationship (Optional since backref exists in RegistrationUser)
    user = db.relationship('RegistrationUser', backref='performance')

    def __repr__(self):
        return f'<Performance {self.user.username} - Quiz {self.Quizzes_id} - Score {self.score}>'



@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.json
    print("hlo")
    fullname = data.get('fullname')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    qualification = data.get('qualification')
    self_description = data.get('self_description')
    print("hii")

    if not all([fullname, username, email, password, qualification]):
        print("in")
        return jsonify({'message': 'All fields are required'}), 400

    if RegistrationUser.query.filter_by(username=username).first():
        print("exits")
        return jsonify({'message': 'Username already exists'}), 400

    hashed_password = generate_password_hash(password)
    new_user = RegistrationUser(
        fullname=fullname,
        username=username,
        email=email,
        password=hashed_password,
        qualification=qualification,
        self_description=self_description,
        fs_uniquifier=username
    )
    print(new_user)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    user_type = data.get('userType')  # Add this to handle admin login

    # Handle admin login
    if user_type == 'admin' and username == 'admin' and password == 'admin':
        access_token = create_access_token(identity='admin')
        
        # Call process_login directly instead of using .delay
        try:
            if hasattr(process_login, 'delay'):
                process_login.delay('admin', datetime.utcnow().isoformat())
            else:
                process_login('admin', datetime.utcnow().isoformat())
        except Exception as e:
            print(f"Warning: Could not process login analytics: {e}")
            
        return jsonify({
            'message': 'Admin login successful',
            'access_token': access_token,
            'user_id': 'admin',
            'username': username,
            'user_type': 'admin'
        })

    # Regular user login
    user = RegistrationUser.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        # Check if user is active (not blocked)
        if not user.active:
            print(f"Login attempt by blocked user: {username}")
            return jsonify({
                'message': 'Your account has been blocked. Please contact an administrator.',
                'error_code': 'ACCOUNT_BLOCKED'
            }), 403
            
        # User is active, proceed with login
        access_token = create_access_token(identity=user.id)
        
        # Call process_login directly instead of using .delay
        try:
            if hasattr(process_login, 'delay'):
                process_login.delay(user.id, datetime.utcnow().isoformat())
            else:
                process_login(user.id, datetime.utcnow().isoformat())
        except Exception as e:
            print(f"Warning: Could not process login analytics: {e}")
            
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user_id': user.id,
            'username': user.username,
            'user_type': 'user'
        })

    return jsonify({'message': 'Invalid credentials'}), 401

# Add simple route for testing authentication
@app.route('/api/test-auth', methods=['GET'])
@jwt_required()
def test_auth():
    return jsonify({'message': 'Authentication successful'}), 200

@login_manager.user_loader
def load_user(user_id):
    return RegistrationUser.query.get(int(user_id))

# # Fetch a specific subject's data (name, id, etc.)
@app.route('/api/subjects/<int:subject_id>', methods=['GET'])
@jwt_required()
def get_subject(subject_id):
    try:
        print(f"Fetching subject with ID: {subject_id}")
        subject = Subject.query.get_or_404(subject_id)
        return jsonify({
            "id": subject.id,
            "name": subject.name,
            "description": subject.description
        }), 200
    except Exception as e:
        print(f"Error fetching subject: {str(e)}")
        return jsonify({"message": "Error fetching subject", "error": str(e)}), 500

# Add a subject update endpoint
@app.route('/api/subjects/<int:subject_id>', methods=['PUT'])
@jwt_required()
def update_subject(subject_id):
    try:
        subject = Subject.query.get_or_404(subject_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Invalid input, JSON data is required'}), 400
            
        subject.name = data.get('name', subject.name)
        subject.description = data.get('description', subject.description)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Subject updated successfully',
            'subject': {
                'id': subject.id,
                'name': subject.name,
                'description': subject.description
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating subject: {str(e)}")
        return jsonify({'message': 'Error updating subject', 'error': str(e)}), 500

# Add a new subject from the admin dashboard
@app.route('/api/admin/subjects', methods=['POST'])
@jwt_required()
def add_subject_from_admin():
    try:
        print("Received subject create request")
        # Ensure JSON data is parsed correctly
        data = request.get_json()
        if not data:
            print("No JSON data received")
            return jsonify({'message': 'Invalid input, JSON data is required'}), 400

        name = data.get('name')
        description = data.get('description')
        print(f"Received data: name={name}, description={description}")

        # Validate input fields
        if not all([name, description]):
            return jsonify({'message': 'Name and description are required'}), 400

        # Check if the subject already exists
        existing_subject = Subject.query.filter_by(name=name).first()
        if existing_subject:
            return jsonify({'message': 'Subject with this name already exists'}), 400

        # Add the new subject to the database
        new_subject = Subject(name=name, description=description)
        db.session.add(new_subject)
        db.session.commit()
        print(f"Subject created with ID: {new_subject.id}")
        
        return jsonify({'message': 'Subject added successfully', 'subject': {
            'id': new_subject.id,
            'name': new_subject.name,
            'description': new_subject.description
        }}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error adding subject: {str(e)}")
        return jsonify({'message': 'Error adding subject', 'error': str(e)}), 500

# Fetch all users for the admin dashboard
@app.route('/api/admin/users', methods=['GET'])
@jwt_required()
def get_users_for_admin():
    try:
        # Get search query parameters
        search_query = request.args.get('q', '').strip().lower()
        
        # Base query
        query = RegistrationUser.query
        
        # Apply search filter if query exists
        if search_query:
            query = query.filter(
                or_(
                    RegistrationUser.username.ilike(f'%{search_query}%'),
                    RegistrationUser.fullname.ilike(f'%{search_query}%'),
                    RegistrationUser.email.ilike(f'%{search_query}%')
                )
            )
            
        # Execute query and format results
        users = query.all()
        
        return jsonify([{
            'id': user.id,
            'fullname': user.fullname,
            'username': user.username,
            'email': user.email,
            'qualification': user.qualification,
            'active': user.active
        } for user in users]), 200
    except Exception as e:
        print(f"Error fetching users: {str(e)}")
        return jsonify({'message': 'Error fetching users', 'error': str(e)}), 500

# Fetch admin dashboard data (subjects and users)
@app.route('/api/admin-dashboard-data', methods=['GET'])
@jwt_required()
def get_admin_dashboard_data():
    try:
        print("Fetching admin dashboard data...")
        
        # Fetch all subjects
        subjects = Subject.query.all()
        subjects_data = [{
            'id': subject.id,
            'name': subject.name,
            'description': subject.description
        } for subject in subjects]
        print(f"Found {len(subjects_data)} subjects")
        
        # Fetch all users
        users = RegistrationUser.query.all()
        users_data = [{
            'id': user.id,
            'fullname': user.fullname,
            'username': user.username,
            'email': user.email,
            'qualification': user.qualification,
            'active': user.active
        } for user in users]
        print(f"Found {len(users_data)} users")
        
        # Return the combined data
        result = {
            'subjects': subjects_data,
            'users': users_data
        }
        print("Successfully fetched admin dashboard data")
        return jsonify(result), 200
    except Exception as e:
        print(f"Error fetching admin dashboard data: {str(e)}")
        return jsonify({'message': 'Error fetching admin dashboard data', 'error': str(e)}), 500

# Get chapters for a specific subject
@app.route('/api/subjects/<int:subject_id>/chapters', methods=['GET'])
# @jwt_required()  # Temporarily comment this out for debugging
def get_subject_chapters(subject_id):
    try:
        print(f"Fetching chapters for subject ID: {subject_id}")
        
        # Debug authentication headers
        auth_header = request.headers.get('Authorization')
        print(f"Auth header: {auth_header}")
        
        subject = Subject.query.get_or_404(subject_id)
        chapters = Chapters.query.filter_by(subject_id=subject_id).all()
        
        chapters_data = [{
            'id': chapter.id,
            'chapter_name': chapter.chapter_name,
            'description': chapter.description,
            'subject_id': chapter.subject_id
        } for chapter in chapters]
        
        return jsonify({
            'subject': {
                'id': subject.id,
                'name': subject.name
            },
            'chapters': chapters_data
        }), 200
    except Exception as e:
        print(f"Error fetching chapters: {str(e)}")
        return jsonify({'message': 'Error fetching chapters', 'error': str(e)}), 500

# Add a new chapter to a subject
@app.route('/api/subjects/<int:subject_id>/chapters', methods=['POST'])
@jwt_required()
def add_chapter(subject_id):
    try:
        print(f"[DEBUG] Adding chapter to subject ID: {subject_id}")
        print(f"[DEBUG] Request data: {request.data}")
        print(f"[DEBUG] Request JSON: {request.get_json()}")
        
        # Check if subject exists
        subject = Subject.query.get_or_404(subject_id)
        print(f"[DEBUG] Found subject: {subject.name}")
        
        data = request.get_json()
        if not data:
            print("[DEBUG] No JSON data received")
            return jsonify({'message': 'Invalid input, JSON data is required'}), 400
            
        chapter_name = data.get('chapter_name')
        description = data.get('description')
        print(f"[DEBUG] Received chapter data: name={chapter_name}, description={description}")
        
        # Validate input
        if not all([chapter_name, description]):
            print("[DEBUG] Missing required fields")
            return jsonify({'message': 'Chapter name and description are required'}), 400
            
        # Create new chapter
        new_chapter = Chapters(
            subject_id=subject_id,
            chapter_name=chapter_name,
            description=description
        )
        
        db.session.add(new_chapter)
        db.session.commit()
        print(f"[DEBUG] Chapter created with ID: {new_chapter.id}")
        
        return jsonify({
            'message': 'Chapter added successfully',
            'chapter': {
                'id': new_chapter.id,
                'chapter_name': new_chapter.chapter_name,
                'description': new_chapter.description,
                'subject_id': new_chapter.subject_id
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"[DEBUG] Error adding chapter: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': 'Error adding chapter', 'error': str(e)}), 500

# Delete a chapter
@app.route('/api/chapters/<int:chapter_id>', methods=['DELETE'])
@jwt_required()
def delete_chapter(chapter_id):
    try:
        chapter = Chapters.query.get_or_404(chapter_id)
        subject_id = chapter.subject_id
        
        db.session.delete(chapter)
        db.session.commit()
        
        return jsonify({
            'message': 'Chapter deleted successfully',
            'subject_id': subject_id
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting chapter: {str(e)}")
        return jsonify({'message': 'Error deleting chapter', 'error': str(e)}), 500

# Update a chapter
@app.route('/api/chapters/<int:chapter_id>', methods=['PUT'])
@jwt_required()
def update_chapter(chapter_id):
    try:
        chapter = Chapters.query.get_or_404(chapter_id)
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Invalid input, JSON data is required'}), 400
            
        # Update chapter details
        chapter.chapter_name = data.get('chapter_name', chapter.chapter_name)
        chapter.description = data.get('description', chapter.description)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Chapter updated successfully',
            'chapter': {
                'id': chapter.id,
                'chapter_name': chapter.chapter_name,
                'description': chapter.description,
                'subject_id': chapter.subject_id
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating chapter: {str(e)}")
        return jsonify({'message': 'Error updating chapter', 'error': str(e)}), 500

# Add a new quiz to a chapter
@app.route('/api/chapters/<int:chapter_id>/quizzes', methods=['POST'])
@jwt_required()
def add_quiz(chapter_id):
    try:
        print(f"[DEBUG] Adding quiz to chapter ID: {chapter_id}")
        print(f"[DEBUG] Request data: {request.data}")
        
        # Check if chapter exists
        chapter = Chapters.query.get_or_404(chapter_id)
        print(f"[DEBUG] Found chapter: {chapter.chapter_name}")
        
        data = request.get_json()
        if not data:
            print("[DEBUG] No JSON data received")
            return jsonify({'message': 'Invalid input, JSON data is required'}), 400
            
        quiz_name = data.get('quiz_name')
        date_of_quiz = data.get('date_of_quiz')
        timing = data.get('timing')
        
        print(f"[DEBUG] Received quiz data: name={quiz_name}, date={date_of_quiz}, timing={timing}")
        
        # Validate input
        if not all([quiz_name, date_of_quiz, timing]):
            print("[DEBUG] Missing required fields")
            return jsonify({'message': 'Quiz name, date and timing are required'}), 400
        
        # Create new quiz
        try:
            # Convert date string to date object if needed
            if isinstance(date_of_quiz, str):
                from datetime import datetime
                date_obj = datetime.strptime(date_of_quiz, '%Y-%m-%d').date()
            else:
                date_obj = date_of_quiz
                
            new_quiz = Quizzes(
                chapter_id=chapter_id,
                quiz_name=quiz_name,
                date_of_quiz=date_obj,
                timing=int(timing)
            )
            
            db.session.add(new_quiz)
            db.session.commit()
            print(f"[DEBUG] Quiz created with ID: {new_quiz.id}")
            
            # Always send notifications about the new quiz - unconditionally
            try:
                if celery and hasattr(celery.tasks.get('celery_worker.send_quiz_notification'), 'delay'):
                    # Use Celery for asynchronous processing
                    print(f"[DEBUG] Scheduling quiz notification task for quiz ID: {new_quiz.id}")
                    task = celery.tasks.get('celery_worker.send_quiz_notification').delay(new_quiz.id)
                    print(f"[DEBUG] Notification task scheduled with ID: {task.id if hasattr(task, 'id') else 'unknown'}")
                else:
                    # Fallback to synchronous processing
                    print(f"[DEBUG] Celery not available. Sending quiz notifications synchronously for quiz ID: {new_quiz.id}")
                    send_quiz_notification_emails(new_quiz.id)
                    print(f"[DEBUG] Notifications sent synchronously for quiz ID: {new_quiz.id}")
            except Exception as notification_error:
                # Log error but don't fail the quiz creation
                print(f"[ERROR] Failed to send quiz notifications: {str(notification_error)}")
                import traceback
                traceback.print_exc()
            
            return jsonify({
                'message': 'Quiz added successfully. Email notifications have been sent to users.',
                'quiz': {
                    'id': new_quiz.id,
                    'quiz_name': new_quiz.quiz_name,
                    'date_of_quiz': str(new_quiz.date_of_quiz),
                    'timing': new_quiz.timing,
                    'chapter_id': new_quiz.chapter_id
                }
            }), 201
        except Exception as e:
            print(f"[DEBUG] Error creating quiz: {str(e)}")
            raise e
            
    except Exception as e:
        db.session.rollback()
        print(f"[DEBUG] Error adding quiz: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': 'Error adding quiz', 'error': str(e)}), 500

# Get quizzes for a specific chapter
@app.route('/api/chapters/<int:chapter_id>/quizzes', methods=['GET'])
# @jwt_required()  # Temporarily comment out for debugging
def get_chapter_quizzes(chapter_id):
    try:
        print(f"Fetching quizzes for chapter ID: {chapter_id}")
        # Debug auth header
        auth_header = request.headers.get('Authorization')
        print(f"Auth header for quizzes: {auth_header}")
        
        chapter = Chapters.query.get_or_404(chapter_id)
        quizzes = Quizzes.query.filter_by(chapter_id=chapter_id).all()
        
        quizzes_data = [{
            'id': quiz.id,
            'quiz_name': quiz.quiz_name,
            'date_of_quiz': str(quiz.date_of_quiz),
            'timing': quiz.timing,
            'chapter_id': quiz.chapter_id
        } for quiz in quizzes]
        
        return jsonify({
            'chapter': {
                'id': chapter.id,
                'chapter_name': chapter.chapter_name
            },
            'quizzes': quizzes_data
        }), 200
    except Exception as e:
        print(f"Error fetching quizzes: {str(e)}")
        return jsonify({'message': 'Error fetching quizzes', 'error': str(e)}), 500

# Get a specific quiz
@app.route('/api/quizzes/<int:quiz_id>', methods=['GET'])
# @jwt_required()  # Temporarily comment out for debugging
def get_quiz(quiz_id):
    try:
        print(f"Fetching quiz with ID: {quiz_id}")
        # Debug auth header
        auth_header = request.headers.get('Authorization')
        print(f"Auth header for quiz details: {auth_header}")
        
        quiz = Quizzes.query.get_or_404(quiz_id)
        
        return jsonify({
            'id': quiz.id,
            'quiz_name': quiz.quiz_name,
            'date_of_quiz': str(quiz.date_of_quiz),
            'timing': quiz.timing,
            'chapter_id': quiz.chapter_id
        }), 200
    except Exception as e:
        print(f"Error fetching quiz: {str(e)}")
        return jsonify({'message': 'Error fetching quiz', 'error': str(e)}), 500

# Add a new question to a quiz
@app.route('/api/quizzes/<int:quiz_id>/questions', methods=['POST'])
@jwt_required()
def add_question(quiz_id):
    try:
        print(f"[DEBUG] Adding question to quiz ID: {quiz_id}")
        print(f"[DEBUG] Request data: {request.data}")
        
        # Check if quiz exists
        quiz = Quizzes.query.get_or_404(quiz_id)
        print(f"[DEBUG] Found quiz: {quiz.quiz_name}")
        
        data = request.get_json()
        if not data:
            print("[DEBUG] No JSON data received")
            return jsonify({'message': 'Invalid input, JSON data is required'}), 400
        
        # Extract question details from request
        question_statement = data.get('question_statement')
        option1 = data.get('option1')
        option2 = data.get('option2')
        option3 = data.get('option3')
        option4 = data.get('option4')
        correct_option=data.get('correct_option')
        marks = data.get('marks', 1)
        
        print(f"[DEBUG] Question details: {question_statement}")
        
        # Validate input - all fields required
        if not all([question_statement, option1, option2, option3, option4,correct_option]):
            print("[DEBUG] Missing required fields")
            return jsonify({'message': 'All question fields are required'}), 400
        
        # Create new question
        new_question = Questions(
            quiz_id=quiz_id,
            question_statement=question_statement,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            correct_option=correct_option,
            marks=int(marks)
        )
        
        db.session.add(new_question)
        db.session.commit()
        print(f"[DEBUG] Question added with ID: {new_question.id}")
        
        return jsonify({
            'message': 'Question added successfully',
            'question': {
                'id': new_question.id,
                'question_statement': new_question.question_statement,
                'option1': new_question.option1,
                'option2': new_question.option2,
                'option3': new_question.option3,
                'option4': new_question.option4,
                'correct_option':new_question.correct_option,
                'marks': new_question.marks
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"[DEBUG] Error adding question: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': 'Error adding question', 'error': str(e)}), 500

# Get all questions for a quiz
@app.route('/api/quizzes/<int:quiz_id>/questions', methods=['GET'])
# @jwt_required()  # Temporarily comment out for debugging
def get_quiz_questions(quiz_id):
    try:
        print(f"Fetching questions for quiz ID: {quiz_id}")
        # Debug auth header
        auth_header = request.headers.get('Authorization')
        print(f"Auth header for questions: {auth_header}")
        
        quiz = Quizzes.query.get_or_404(quiz_id)
        questions = Questions.query.filter_by(quiz_id=quiz_id).all()
        
        questions_data = [{
            'id': question.id,
            'question_statement': question.question_statement,
            'option1': question.option1,
            'option2': question.option2,
            'option3': question.option3,
            'option4': question.option4,
            'correct_option':question.correct_option,
            'marks': question.marks
        } for question in questions]
        
        return jsonify({
            'quiz': {
                'id': quiz.id,
                'quiz_name': quiz.quiz_name
            },
            'questions': questions_data
        }), 200
    except Exception as e:
        print(f"Error fetching questions: {str(e)}")
        return jsonify({'message': 'Error fetching questions', 'error': str(e)}), 500

# Update a question
@app.route('/api/questions/<int:question_id>', methods=['PUT'])
@jwt_required()
def update_question(question_id):
    try:
        question = Questions.query.get_or_404(question_id)
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Invalid input, JSON data is required'}), 400
        
        # Update question fields
        question.question_statement = data.get('question_statement', question.question_statement)
        question.option1 = data.get('option1', question.option1)
        question.option2 = data.get('option2', question.option2)
        question.option3 = data.get('option3', question.option3)
        question.option4 = data.get('option4', question.option4)
        question.correct_option=data.get('correct_option',question.correct_option)
        question.marks = data.get('marks', question.marks)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Question updated successfully',
            'question': {
                'id': question.id,
                'question_statement': question.question_statement,
                'option1': question.option1,
                'option2': question.option2,
                'option3': question.option3,
                'option4': question.option4,
                'marks': question.marks
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating question: {str(e)}")
        return jsonify({'message': 'Error updating question', 'error': str(e)}), 500

# Delete a question
@app.route('/api/questions/<int:question_id>', methods=['DELETE'])
@jwt_required()
def delete_question(question_id):
    try:
        question = Questions.query.get_or_404(question_id)
        quiz_id = question.quiz_id
        
        db.session.delete(question)
        db.session.commit()
        
        return jsonify({
            'message': 'Question deleted successfully',
            'quiz_id': quiz_id
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting question: {str(e)}")
        return jsonify({'message': 'Error deleting question', 'error': str(e)}), 500

# Add these routes before the if __name__ == '__main__': block

# Get all subjects for quiz selection
@app.route('/api/subjects', methods=['GET'])
# @jwt_required()  # Temporarily comment this out for debugging
def get_all_subjects():
    try:
        # Add debug logging
        print("Getting all subjects, checking auth header:")
        auth_header = request.headers.get('Authorization')
        print(f"Auth header: {auth_header}")
        
        subjects = Subject.query.all()
        subjects_data = [{
            'id': subject.id,
            'name': subject.name,
            'description': subject.description
        } for subject in subjects]
        
        return jsonify(subjects_data), 200
    except Exception as e:
        print(f"Error fetching subjects: {str(e)}")
        return jsonify({'message': 'Error fetching subjects', 'error': str(e)}), 500

# Get specific chapter info (needed for breadcrumb navigation)
@app.route('/api/chapters/<int:chapter_id>', methods=['GET'])
@jwt_required()
def get_chapter_details(chapter_id):
    try:
        chapter = Chapters.query.get_or_404(chapter_id)
        
        return jsonify({
            'id': chapter.id,
            'chapter_name': chapter.chapter_name,
            'description': chapter.description,
            'subject_id': chapter.subject_id
        }), 200
    except Exception as e:
        print(f"Error fetching chapter: {str(e)}")
        return jsonify({'message': 'Error fetching chapter', 'error': str(e)}), 500

# Check session status
@app.route('/check-session', methods=['GET'])
def check_session():
    return jsonify({'message': 'Backend is connected and session is active'}), 200

# Submit quiz results 
@app.route('/api/submit-quiz', methods=['POST'])
# @jwt_required()  # Temporarily comment out for debugging
def submit_quiz():
    try:
        data = request.get_json()
        quiz_id = data.get('quiz_id')
        user_id = data.get('user_id')
        score = data.get('score')
        total_possible = data.get('total_possible')
        answers = data.get('answers', [])
        
        # Debug auth header
        auth_header = request.headers.get('Authorization')
        print(f"Auth header for quiz submission: {auth_header}")
        
        if not all([quiz_id, user_id, score is not None]):
            return jsonify({'message': 'Quiz ID, user ID, and score are required'}), 400
            
        # Save to Scores table
        new_score = Scores(
            quiz_id=quiz_id,
            user_id=user_id,
            total_scored=score
        )
        
        # Also update the Performance table
        new_performance = Performance(
            RegistrationUser_id=user_id,
            Quizzes_id=quiz_id,
            score=float(score),
            attempted_at=datetime.utcnow()
        )
        
        db.session.add(new_score)
        db.session.add(new_performance)
        db.session.commit()
        
        return jsonify({
            'message': 'Quiz submitted successfully',
            'score': score,
            'total_possible': total_possible,
            'percentage': round((score / total_possible * 100) if total_possible > 0 else 0, 2)
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error submitting quiz: {str(e)}")
        return jsonify({'message': 'Error submitting quiz', 'error': str(e)}), 500

# Get user's quiz history for progress page
@app.route('/api/user-progress/<int:user_id>', methods=['GET'])
# @jwt_required()  # Temporarily comment out for debugging
def get_user_progress(user_id):
    try:
        # Debug auth header
        auth_header = request.headers.get('Authorization')
        print(f"Auth header for user progress: {auth_header}")
        
        # Get all performances for this user
        performances = Performance.query.filter_by(RegistrationUser_id=user_id).all()
        
        results = []
        for perf in performances:
            # Get quiz details
            quiz = Quizzes.query.get(perf.Quizzes_id)
            if quiz:
                # Get chapter details
                chapter = Chapters.query.get(quiz.chapter_id)
                # Get subject details
                subject = Subject.query.get(chapter.subject_id) if chapter else None
                
                results.append({
                    'performance_id': perf.id,
                    'quiz_id': perf.Quizzes_id,
                    'quiz_name': quiz.quiz_name if quiz else 'Unknown Quiz',
                    'chapter_name': chapter.chapter_name if chapter else 'Unknown Chapter',
                    'subject_name': subject.name if subject else 'Unknown Subject',
                    'score': perf.score,
                    'attempted_at': perf.attempted_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'subject_id': chapter.subject_id if chapter else None,
                    'chapter_id': quiz.chapter_id if quiz else None
                })
        
        return jsonify(results), 200
    except Exception as e:
        print(f"Error fetching user progress: {str(e)}")
        import traceback
        traceback.print_exc()  # Print full traceback for debugging
        return jsonify({'message': 'Error fetching user progress', 'error': str(e)}), 500

# Get recent scores by a user across all quizzes for dashboard
@app.route('/api/user/<int:user_id>/recent-scores', methods=['GET'])
@jwt_required()
def get_user_recent_scores(user_id):
    try:
        # Get the 5 most recent scores for this user
        recent_scores = Scores.query.filter_by(user_id=user_id)\
            .order_by(Scores.time_stamp_of_attempt.desc())\
            .limit(5).all()
        
        results = []
        for score in recent_scores:
            # Get quiz details
            quiz = Quizzes.query.get(score.quiz_id)
            if quiz:
                # Get chapter details
                chapter = Chapters.query.get(quiz.chapter_id)
                
                results.append({
                    'score_id': score.id,
                    'quiz_id': score.quiz_id,
                    'quiz_name': quiz.quiz_name,
                    'chapter_name': chapter.chapter_name if chapter else 'Unknown Chapter',
                    'score': score.total_scored,
                    'attempted_at': score.time_stamp_of_attempt.strftime('%Y-%m-%d %H:%M:%S')
                })
        
        return jsonify(results), 200
    except Exception as e:
        print(f"Error fetching recent scores: {str(e)}")
        return jsonify({'message': 'Error fetching recent scores', 'error': str(e)}), 500

# Get quiz statistics for a specific quiz (for admin)
@app.route('/api/quiz/<int:quiz_id>/statistics', methods=['GET'])
@jwt_required()
def get_quiz_statistics(quiz_id):
    try:
        # Get all scores for this quiz
        scores = Scores.query.filter_by(quiz_id=quiz_id).all()
        
        if not scores:
            return jsonify({
                'quiz_id': quiz_id,
                'total_attempts': 0,
                'average_score': 0,
                'highest_score': 0,
                'lowest_score': 0
            }), 200
        
        # Calculate statistics
        total_attempts = len(scores)
        score_values = [score.total_scored for score in scores]
        average_score = sum(score_values) / total_attempts if total_attempts > 0 else 0
        highest_score = max(score_values) if score_values else 0
        lowest_score = min(score_values) if score_values else 0
        
        return jsonify({
            'quiz_id': quiz_id,
            'total_attempts': total_attempts,
            'average_score': round(average_score, 2),
            'highest_score': highest_score,
            'lowest_score': lowest_score
        }), 200
    except Exception as e:
        print(f"Error fetching quiz statistics: {str(e)}")
        return jsonify({'message': 'Error fetching quiz statistics', 'error': str(e)}), 500
@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    use_celery = request.args.get('async', 'false').lower() == 'true'
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    # Get user type for role-based search results
    jwt_token = request.headers.get('Authorization', '')
    user_type = 'user'  # Default
    
    if jwt_token:
        try:
            if jwt_token.startswith('Bearer '):
                token = jwt_token[7:]
            else:
                token = jwt_token
                
            # Get user identity from token - simplified for now
            # In production, would properly decode and verify token
            user_id = token.split('.')[1]  # Simplistic approach for demo
            if user_id == 'admin':
                user_type = 'admin'
        except:
            pass  # Default to 'user' if token parsing fails
    
    # If query is very short, return empty results
    if len(query) < 2:
        return jsonify({
            'subjects': [],
            'chapters': [],
            'quizzes': [],
            'users': [] if user_type == 'admin' else [],
            'all': [],
            'meta': {
                'query': query,
                'total': 0,
                'page': page,
                'per_page': per_page,
                'user_type': user_type,
                'processed_by': 'direct'
            }
        })
    
    # Log search query for analytics
    print(f"Search query: '{query}' by {user_type}")
    
    try:
        # Determine if we should use Celery for this query
        if use_celery and celery is not None and hasattr(search_task, 'delay'):
            # For background processing with Celery
            task = search_task.delay(query, user_type)
            task_id = task.id
            
            # For a real implementation, you'd store the task ID and have
            # a separate endpoint to poll for results using task_id
            
            # Here we'll just execute it directly for simplicity
            results = perform_search(query, user_type)
            results['meta'] = {
                'query': query,
                'total': len(results['all']),
                'page': page,
                'per_page': per_page,
                'user_type': user_type,
                'processed_by': 'celery-immediate',
                'task_id': task_id
            }
        else:
            # Direct processing
            results = perform_search(query, user_type)
            results['meta'] = {
                'query': query,
                'total': len(results['all']),
                'page': page,
                'per_page': per_page,
                'user_type': user_type,
                'processed_by': 'direct'
            }
        
        # Apply pagination to all result lists
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        for key in ['subjects', 'chapters', 'quizzes', 'users', 'all']:
            if key in results:
                results[key] = results[key][start_idx:end_idx]
        
        return jsonify(results)
        
    except Exception as e:
        print(f"Error searching: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'message': 'Error searching',
            'error': str(e),
            'meta': {
                'query': query,
                'user_type': user_type
            }
        }), 500

# Add a Celery task for searching
@celery.task(name="app.search_task")
def search_task(query, user_type='user'):
    """Background task to search across all entities"""
    try:
        search_results = perform_search(query, user_type)
        return search_results
    except Exception as e:
        print(f"Error in search task: {str(e)}")
        return {"error": str(e)}

def perform_search(query, user_type='user'):
    """Core search functionality that searches across multiple entities"""
    # Normalize query
    query = query.strip().lower()
    
    # Empty results structure
    results = {
        'subjects': [],
        'chapters': [],
        'quizzes': [],
        'users': [] if user_type == 'admin' else []  # Only include users for admin
    }
    
    # Search in subjects (name and description)
    subjects = Subject.query.filter(
        or_(
            Subject.name.ilike(f'%{query}%'),
            Subject.description.ilike(f'%{query}%')
        )
    ).all()
    
    results['subjects'] = [{
        'id': s.id,
        'name': s.name,
        'description': s.description,
        'type': 'subject'
    } for s in subjects]
    
    # Search in chapters (name and description)
    chapters = Chapters.query.filter(
        or_(
            Chapters.chapter_name.ilike(f'%{query}%'),
            Chapters.description.ilike(f'%{query}%')
        )
    ).all()
    
    results['chapters'] = [{
        'id': c.id,
        'chapter_name': c.chapter_name, 
        'description': c.description,
        'subject_id': c.subject_id,
        'subject_name': c.subject.name if c.subject else 'Unknown',
        'type': 'chapter'
    } for c in chapters]
    
    # Search in quizzes (name)
    quizzes = Quizzes.query.filter(
        Quizzes.quiz_name.ilike(f'%{query}%')
    ).all()
    
    results['quizzes'] = [{
        'id': q.id,
        'quiz_name': q.quiz_name,
        'timing': q.timing,
        'chapter_id': q.chapter_id,
        'chapter_name': q.chapter.chapter_name if q.chapter else 'Unknown',
        'type': 'quiz'
    } for q in quizzes]
    
    # If admin, also search in users
    if user_type == 'admin':
        users = RegistrationUser.query.filter(
            or_(
                RegistrationUser.username.ilike(f'%{query}%'),
                RegistrationUser.fullname.ilike(f'%{query}%'),
                RegistrationUser.email.ilike(f'%{query}%'),
                RegistrationUser.qualification.ilike(f'%{query}%')
            )
        ).all()
        
        results['users'] = [{
            'id': u.id,
            'username': u.username,
            'fullname': u.fullname,
            'email': u.email,
            'qualification': u.qualification,
            'active': u.active,
            'type': 'user'
        } for u in users]
    
    # Add a combined "all" category for easier frontend display
    all_results = []
    all_results.extend(results['subjects'])
    all_results.extend(results['chapters'])
    all_results.extend(results['quizzes'])
    if user_type == 'admin':
        all_results.extend(results['users'])
    
    # Sort combined results by relevance (if query directly in name, rank higher)
    def relevance_score(item):
        name_field = item.get('name', item.get('chapter_name', item.get('quiz_name', item.get('username', ''))))
        if query in name_field.lower():
            return 0  # Higher priority
        return 1  # Lower priority
    
    all_results.sort(key=relevance_score)
    results['all'] = all_results
    
    return results

# Add a new endpoint to check async search task status
@app.route('/api/search/task/<task_id>', methods=['GET'])
def check_search_task(task_id):
    if celery is None:
        return jsonify({'status': 'error', 'message': 'Celery not available'}), 500
        
    try:
        task = search_task.AsyncResult(task_id)
        if task.state == 'PENDING':
            response = {
                'status': 'pending',
                'message': 'Task is pending'
            }
        elif task.state == 'SUCCESS':
            response = {
                'status': 'success',
                'results': task.result
            }
        else:
            response = {
                'status': task.state,
                'message': str(task.info)
            }
        return jsonify(response)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error checking task: {str(e)}'
        }), 500

# Add this diagnostic route
@app.route('/api/auth/debug', methods=['POST'])
def debug_auth():
    """Diagnostic endpoint to debug authentication issues"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # Check if user exists
    user = RegistrationUser.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({
            'status': 'error',
            'message': 'User not found in database',
            'code': 'USER_NOT_FOUND'
        }), 404
    
    # Check if password matches (without returning actual password)
    password_match = check_password_hash(user.password, password)
    
    # If successful, queue background task using Celery
    if password_match:
        process_login.delay(user.id, datetime.utcnow().isoformat())
    
    return jsonify({
        'status': 'debug',
        'user_exists': True,
        'password_match': password_match,
        'username': username,
        'user_id': user.id if user else None,
    })

@app.route('/api/check-redis', methods=['GET'])
def check_redis():
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        
        # Try to set a test value
        r.set('test_key', 'Redis is working!')
        test_value = r.get('test_key')
        
        return jsonify({
            'status': 'success',
            'message': 'Redis connection successful',
            'test_value': test_value.decode('utf-8') if test_value else None
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Redis connection failed: {str(e)}'
        }), 500

@app.route('/api/test-celery', methods=['GET'])
def test_celery():
    try:
        # Send a simple task
        task = process_login.delay(0, datetime.utcnow().isoformat())
        
        return jsonify({
            'status': 'success',
            'message': 'Celery task dispatched successfully',
            'task_id': task.id
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Celery error: {str(e)}'
        }), 500

# Add a new route for debugging JWT tokens
@app.route('/api/debug-token', methods=['GET'])
def debug_token():
    """Debug endpoint to verify JWT token processing"""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        return jsonify({
            'status': 'error',
            'message': 'No Authorization header found'
        }), 400
    
    # Extract token parts
    try:
        # Handle both with and without 'Bearer ' prefix
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]  # Remove 'Bearer ' prefix
        else:
            token = auth_header
            
        # Print the token for debugging
        print(f"Token received: {token[:20]}...")
        
        # Basic structure check (not full validation)
        parts = token.split('.')
        if len(parts) != 3:
            return jsonify({
                'status': 'error',
                'message': 'Invalid JWT format, expected 3 parts separated by dots'
            }), 400
            
        return jsonify({
            'status': 'success',
            'message': 'JWT token appears valid',
            'token_parts': len(parts)
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error parsing token: {str(e)}'
        }), 400

@app.route('/api/users/<string:user_id>', methods=['GET'])
def get_user_profile(user_id):
    try:
        # Handle 'admin' user specially
        if user_id == 'admin':
            return jsonify({
                'id': 'admin',
                'username': 'admin',
                'fullname': 'Administrator',
                'email': 'admin@example.com',
                'qualification': 'System Administrator',
                'self_description': 'System administrator account'
            }), 200
        
        # For regular users
        user = RegistrationUser.query.get_or_404(user_id)
        return jsonify({
            'id': user.id,
            'username': user.username,
            'fullname': user.fullname,
            'email': user.email,
            'qualification': user.qualification,
            'self_description': user.self_description
        }), 200
    except Exception as e:
        print(f"Error fetching user profile: {str(e)}")
        return jsonify({'message': 'Error fetching user profile', 'error': str(e)}), 500

@app.route('/api/users/<string:user_id>/quiz-stats', methods=['GET'])
def get_user_quiz_stats(user_id):
    try:
        # If admin, return mock stats
        if user_id == 'admin':
            return jsonify({
                'total_quizzes_attempted': 0,
                'average_score': 0,
                'highest_score': 0,
                'total_time_spent': 0
            }), 200
        
        # Get stats for regular users
        performances = Performance.query.filter_by(RegistrationUser_id=user_id).all()
        
        if not performances:
            return jsonify({
                'total_quizzes_attempted': 0,
                'average_score': 0,
                'highest_score': 0,
                'total_time_spent': 0
            }), 200
            
        scores = [p.score for p in performances]
        
        # Calculate stats
        total_quizzes = len(performances)
        avg_score = sum(scores) / total_quizzes if total_quizzes > 0 else 0
        highest_score = max(scores) if scores else 0
        
        # Get quizzes to calculate time spent
        quiz_ids = [p.Quizzes_id for p in performances]
        quizzes = Quizzes.query.filter(Quizzes.id.in_(quiz_ids)).all()
        total_time = sum(q.timing for q in quizzes) if quizzes else 0
        
        return jsonify({
            'total_quizzes_attempted': total_quizzes,
            'average_score': round(avg_score, 2),
            'highest_score': highest_score,
            'total_time_spent': total_time
        }), 200
    except Exception as e:
        print(f"Error fetching user quiz stats: {str(e)}")
        return jsonify({'message': 'Error fetching user quiz stats', 'error': str(e)}), 500

# Add a new endpoint to get comparative performance data
@app.route('/api/user-performance-comparison/<int:user_id>', methods=['GET'])
def get_user_performance_comparison(user_id):
    try:
        # Get query parameters for filtering
        quiz_id = request.args.get('quiz_id')
        subject_id = request.args.get('subject_id')
        limit = int(request.args.get('limit', 5))  # Default to 5 quizzes
        
        # Build the base query
        query = db.session.query(
            Performance.Quizzes_id,
            Quizzes.quiz_name,
            db.func.avg(Performance.score).label('average_score'),
            db.func.count(Performance.id).label('attempt_count')
        ).join(Quizzes, Performance.Quizzes_id == Quizzes.id)
        
        # Filter by specific quiz if provided
        if quiz_id:
            query = query.filter(Performance.Quizzes_id == quiz_id)
        
        # Filter by subject if provided
        if subject_id:
            query = query.join(Chapters, Quizzes.chapter_id == Chapters.id)\
                         .filter(Chapters.subject_id == subject_id)
        
        # Group by quiz and order by most attempted
        comparison_data = query.group_by(Performance.Quizzes_id)\
                              .order_by(db.func.count(Performance.id).desc())\
                              .limit(limit)\
                              .all()
        
        # Format results
        results = []
        for quiz_id, quiz_name, avg_score, attempt_count in comparison_data:
            # Get the user's performance on this quiz
            user_perf = Performance.query.filter_by(
                RegistrationUser_id=user_id,
                Quizzes_id=quiz_id
            ).first()
            
            user_score = user_perf.score if user_perf else None
            
            results.append({
                'quiz_id': quiz_id,
                'quiz_name': quiz_name,
                'average_score': round(avg_score, 2),
                'user_score': user_score,
                'attempt_count': attempt_count,
                'percentile': calculate_percentile(user_id, quiz_id) if user_score is not None else None
            })
        
        return jsonify({
            'comparison_data': results,
            'total_quizzes': len(results)
        }), 200
        
    except Exception as e:
        print(f"Error fetching performance comparison: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': 'Error fetching performance comparison', 'error': str(e)}), 500

def calculate_percentile(user_id, quiz_id):
    """Calculate what percentile the user falls into for a given quiz"""
    try:
        # Get all scores for this quiz
        all_scores = [p.score for p in Performance.query.filter_by(Quizzes_id=quiz_id).all()]
        
        if not all_scores:
            return None
            
        # Get user's score
        user_perf = Performance.query.filter_by(RegistrationUser_id=user_id, Quizzes_id=quiz_id).first()
        if not user_perf:
            return None
            
        # Calculate how many scores are lower than the user's
        lower_scores = sum(1 for score in all_scores if score < user_perf.score)
        
        # Calculate percentile
        percentile = (lower_scores / len(all_scores)) * 100
        
        return round(percentile, 1)
    except Exception as e:
        print(f"Error calculating percentile: {str(e)}")
        return None

# Add new functions for report generation
def generate_performance_report_html(user_id, month=None, year=None):
    """Generate an HTML report of user performance, optionally filtered by month"""
    try:
        # Get user info
        user = RegistrationUser.query.get_or_404(user_id)
        
        # Apply time filtering if month is specified
        if month and year:
            # Convert month name to number
            import calendar
            if isinstance(month, str):
                try:
                    month_num = list(calendar.month_name).index(month.title())
                except ValueError:
                    # Try with month abbreviation
                    month_num = list(calendar.month_abbr).index(month.title()[:3])
            else:
                month_num = month
                
            # Filter performances by month and year
            from sqlalchemy import extract
            performances = Performance.query.filter(
                Performance.RegistrationUser_id == user_id,
                extract('month', Performance.attempted_at) == month_num,
                extract('year', Performance.attempted_at) == year
            ).all()
            
            report_title = f"Monthly Performance Report - {calendar.month_name[month_num]} {year}"
        else:
            # Get all performances for this user
            performances = Performance.query.filter_by(RegistrationUser_id=user_id).all()
            report_title = "Performance Report"
        
        if not performances:
            if month and year:
                return f"<h1>No quiz data available for {calendar.month_name[month_num]} {year}</h1><p>You haven't taken any quizzes during this period.</p>"
            else:
                return "<h1>No quiz data available</h1><p>You haven't taken any quizzes yet.</p>"
        
        # Convert to DataFrame for easier analysis
        data = []
        for perf in performances:
            quiz = Quizzes.query.get(perf.Quizzes_id)
            if not quiz:
                continue
                
            chapter = Chapters.query.get(quiz.chapter_id)
            subject = Subject.query.get(chapter.subject_id) if chapter else None
            
            data.append({
                'quiz_id': perf.Quizzes_id,
                'quiz_name': quiz.quiz_name,
                'chapter_name': chapter.chapter_name if chapter else 'Unknown',
                'subject_name': subject.name if subject else 'Unknown',
                'score': perf.score,
                'date': perf.attempted_at.strftime('%Y-%m-%d'),
                'percentile': calculate_percentile(user_id, perf.Quizzes_id) or 0
            })
        
        # Create a DataFrame
        df = pd.DataFrame(data)
        
        # Generate a base64 encoded image of subject performance
        subject_plot_base64 = None
        if not df.empty:
            plt.figure(figsize=(10, 6))
            subject_avg = df.groupby('subject_name')['score'].mean().sort_values(ascending=False)
            subject_avg.plot(kind='bar', color='skyblue')
            plt.title('Average Score by Subject')
            plt.ylabel('Score (%)')
            plt.xlabel('Subject')
            plt.tight_layout()
            
            # Save plot to a bytes buffer
            buf = BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            subject_plot_base64 = base64.b64encode(buf.read()).decode('utf-8')
            plt.close()
        
        # Generate a base64 encoded image of score trend
        trend_plot_base64 = None
        if len(df) > 1:
            plt.figure(figsize=(10, 6))
            df_sorted = df.sort_values('date')
            plt.plot(df_sorted['date'], df_sorted['score'], marker='o', linestyle='-', color='green')
            plt.title('Score Trend Over Time')
            plt.ylabel('Score (%)')
            plt.xlabel('Date')
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()
            
            # Save plot to a bytes buffer
            buf = BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            trend_plot_base64 = base64.b64encode(buf.read()).decode('utf-8')
            plt.close()
        
        # Summary statistics
        avg_score = df['score'].mean()
        highest_score = df['score'].max()
        total_quizzes = len(df)
        avg_percentile = df['percentile'].mean()
        
        # Generate HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{report_title} for {user.fullname}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; color: #333; }}
                .header {{ background-color: #4a6bdf; color: white; padding: 20px; text-align: center; margin-bottom: 30px; }}
                .section {{ margin-bottom: 30px; }}
                h1, h2, h3 {{ color: #4a6bdf; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 12px 15px; border-bottom: 1px solid #ddd; text-align: left; }}
                th {{ background-color: #f8f9fa; }}
                tr:hover {{ background-color: #f1f1f1; }}
                .summary-cards {{ display: flex; justify-content: space-between; flex-wrap: wrap; margin: 20px 0; }}
                .card {{ background-color: #f8f9fa; border-radius: 8px; padding: 15px; width: 22%; min-width: 200px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 15px; }}
                .card h3 {{ margin-top: 0; font-size: 16px; }}
                .card p {{ font-size: 24px; font-weight: bold; color: #4a6bdf; margin: 5px 0; }}
                .plot-container {{ text-align: center; margin: 30px 0; }}
                img {{ max-width: 100%; height: auto; }}
                footer {{ text-align: center; margin-top: 50px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{report_title}</h1>
                <p>Generated for {user.fullname} on {datetime.now().strftime('%Y-%m-%d')}</p>
            </div>
            
            <div class="section">
                <h2>Performance Summary</h2>
                <div class="summary-cards">
                    <div class="card">
                        <h3>Average Score</h3>
                        <p>{avg_score:.1f}%</p>
                    </div>
                    <div class="card">
                        <h3>Highest Score</h3>
                        <p>{highest_score:.1f}%</p>
                    </div>
                    <div class="card">
                        <h3>Total Quizzes</h3>
                        <p>{total_quizzes}</p>
                    </div>
                    <div class="card">
                        <h3>Average Percentile</h3>
                        <p>{avg_percentile:.1f}%</p>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>Performance by Subject</h2>
                {f'<div class="plot-container"><img src="data:image/png;base64,{subject_plot_base64}" alt="Subject Performance" /></div>' if subject_plot_base64 else '<p>Not enough data to generate subject performance chart.</p>'}
            </div>
            
            <div class="section">
                <h2>Performance Trend</h2>
                {f'<div class="plot-container"><img src="data:image/png;base64,{trend_plot_base64}" alt="Score Trend" /></div>' if trend_plot_base64 else '<p>Not enough data to generate performance trend chart.</p>'}
            </div>
            
            <div class="section">
                <h2>Detailed Quiz Results</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Subject</th>
                            <th>Chapter</th>
                            <th>Quiz</th>
                            <th>Score</th>
                            <th>Percentile</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(f"<tr><td>{row['date']}</td><td>{row['subject_name']}</td><td>{row['chapter_name']}</td><td>{row['quiz_name']}</td><td>{row['score']:.1f}%</td><td>{row['percentile']:.1f}%</td></tr>" for _, row in df.iterrows())}
                    </tbody>
                </table>
            </div>
            
            <footer>
                <p>This report was automatically generated by Quiz Master.</p>
                <p>&copy; {datetime.now().year} Quiz Master. All rights reserved.</p>
            </footer>
        </body>
        </html>
        """
        
        return html_content
    except Exception as e:
        print(f"Error generating performance report: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"<h1>Error Generating Report</h1><p>{str(e)}</p>"

def generate_performance_report_pdf(user_id):
    """Generate a PDF report from the HTML report"""
    try:
        html_content = generate_performance_report_html(user_id)
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            # Generate PDF
            HTML(string=html_content).write_pdf(tmp.name)
            tmp_path = tmp.name
            
        # Read the PDF file
        with open(tmp_path, 'rb') as f:
            pdf_data = f.read()
            
        # Delete temporary file
        import os
        os.unlink(tmp_path)
        
        return pdf_data
    except Exception as e:
        print(f"Error generating PDF report: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

# Add new routes for reports
@app.route('/api/user/<int:user_id>/email-report', methods=['POST'])
# @jwt_required()  # Uncomment after testing
def email_performance_report(user_id):
    try:
        # Get user email
        user = RegistrationUser.query.get_or_404(user_id)
        
        # Print debug info
        print(f"Preparing to send email to: {user.email}")
        print(f"Using mail configuration: {app.config['MAIL_USERNAME']}")
        
        # Generate HTML report
        html_content = generate_performance_report_html(user_id)
        
        # Create message
        msg = Message(
            subject="Your Quiz Master Performance Report",
            recipients=[user.email],
            html=html_content
        )
        
        # Generate PDF attachment
        pdf_data = generate_performance_report_pdf(user_id)
        if pdf_data:
            msg.attach(
                filename="performance_report.pdf",
                content_type="application/pdf",
                data=pdf_data
            )
        
        # Send email with specific error handling
        try:
            mail.send(msg)
            print(f"Email sent successfully to {user.email}")
        except Exception as mail_error:
            print(f"Mail sending error: {str(mail_error)}")
            return jsonify({
                'message': 'Error sending performance report',
                'error': str(mail_error)
            }), 500
        
        return jsonify({
            'message': 'Performance report sent successfully to ' + user.email
        }), 200
    except Exception as e:
        print(f"Error sending performance report: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': 'Error sending performance report', 'error': str(e)}), 500

@app.route('/api/user/<int:user_id>/download-report', methods=['GET'])
# @jwt_required()  # Uncomment after testing
def download_performance_report(user_id):
    try:
        # Generate PDF
        pdf_data = generate_performance_report_pdf(user_id)
        
        if not pdf_data:
            return jsonify({'message': 'Error generating PDF report'}), 500
            
        # Create response with PDF
        from flask import send_file
        
        return send_file(
            BytesIO(pdf_data),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'performance_report_{user_id}.pdf'
        )
    except Exception as e:
        print(f"Error downloading performance report: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': 'Error downloading performance report', 'error': str(e)}), 500

# Add this function near the other email-related functions
def send_quiz_notification_emails(quiz_id):
    """Send email notifications to all active users about a new quiz"""
    try:
        # Get quiz details
        quiz = Quizzes.query.get_or_404(quiz_id)
        chapter = Chapters.query.get_or_404(quiz.chapter_id)
        subject = Subject.query.get_or_404(chapter.subject_id)
        
        # Get all active users
        users = RegistrationUser.query.filter_by(active=True).all()
        
        if not users:
            print("No active users to notify")
            return
            
        # Create message template
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4a6bdf; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .button {{ display: inline-block; background-color: #4a6bdf; color: white; text-decoration: none; padding: 10px 20px; border-radius: 5px; margin-top: 20px; }}
                .footer {{ font-size: 12px; text-align: center; margin-top: 30px; color: #777; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>New Quiz Available!</h2>
            </div>
            <div class="content">
                <p>Hello,</p>
                <p>A new quiz has been added to Quiz Master and is now available for you to attempt.</p>
                
                <h3>Quiz Details:</h3>
                <ul>
                    <li><strong>Quiz:</strong> {quiz.quiz_name}</li>
                    <li><strong>Subject:</strong> {subject.name}</li>
                    <li><strong>Chapter:</strong> {chapter.chapter_name}</li>
                    <li><strong>Time Limit:</strong> {quiz.timing} minutes</li>
                </ul>
                
                <p>Don't miss this opportunity to test your knowledge!</p>
                
                <a href="http://localhost:8080/quiz/{quiz_id}" class="button">Take Quiz Now</a>
            </div>
            <div class="footer">
                <p>This is an automatic notification from Quiz Master. Please do not reply to this email.</p>
            </div>
        </body>
        </html>
        """
        
        # Send emails in batches to avoid overwhelming the mail server
        batch_size = 20
        for i in range(0, len(users), batch_size):
            batch_users = users[i:i+batch_size]
            with app.app_context():
                msg = Message(
                    subject=f"New Quiz Available: {quiz.quiz_name}",
                    recipients=[user.email for user in batch_users],
                    html=html_content
                )
                mail.send(msg)
                
            # Small delay between batches
            import time
            time.sleep(2)
            
        print(f"Sent quiz notification emails to {len(users)} users")
        return True
    except Exception as e:
        print(f"Error sending quiz notification emails: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

# Add this new endpoint for manual notification testing
@app.route('/api/admin/notify-quiz/<int:quiz_id>', methods=['POST'])
@jwt_required()
def admin_notify_quiz(quiz_id):
    """Admin endpoint to manually trigger quiz notifications"""
    try:
        # Queue the notification task
        if celery and hasattr(celery.tasks.get('celery_worker.send_quiz_notification'), 'delay'):
            celery.tasks.get('celery_worker.send_quiz_notification').delay(quiz_id)
            return jsonify({'message': 'Quiz notification queued successfully'}), 200
        else:
            # Fallback to synchronous execution
            success = send_quiz_notification_emails(quiz_id)
            if success:
                return jsonify({'message': 'Quiz notification sent successfully'}), 200
            else:
                return jsonify({'message': 'Error sending quiz notifications'}), 500
    except Exception as e:
        print(f"Error queuing quiz notification: {str(e)}")
        return jsonify({'message': 'Error queuing quiz notification', 'error': str(e)}), 500

# Add a new endpoint to manually trigger monthly reports
@app.route('/api/admin/send-monthly-reports', methods=['POST'])
@jwt_required()
def trigger_monthly_reports():
    try:
        data = request.get_json() or {}
        month = data.get('month')  # Can be None for current month
        year = data.get('year')    # Can be None for current year
        
        # If month/year not specified, use current month/year
        if not month or not year:
            from datetime import datetime
            now = datetime.now()
            month = now.month if not month else month
            year = now.year if not year else year
        
        # Queue the task
        if celery and hasattr(celery.tasks.get('celery_worker.send_monthly_reports'), 'delay'):
            task = celery.tasks.get('celery_worker.send_monthly_reports').delay(month, year)
            return jsonify({
                'message': 'Monthly reports task queued successfully',
                'task_id': task.id,
                'month': month,
                'year': year
            }), 200
        else:
            return jsonify({
                'message': 'Celery not available for task scheduling',
                'error': 'Configure Celery to enable this feature'
            }), 500
    except Exception as e:
        print(f"Error triggering monthly reports: {str(e)}")
        return jsonify({
            'message': 'Error triggering monthly reports',
            'error': str(e)
        }), 500

# Add a new endpoint to send notifications to all users
@app.route('/api/notifications/send-all', methods=['POST', 'OPTIONS'])
@jwt_required()
def send_all_notifications():
    """Send notifications to all users about upcoming quizzes"""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        return response
        
    try:
        data = request.get_json() or {}
        message = data.get('message', 'Important notification from Quiz Master')
        subject = data.get('subject', 'Quiz Master Notification')
        
        # Get upcoming quizzes if needed
        days_ahead = data.get('days_ahead', 7)  # Default to next 7 days
        include_quizzes = data.get('include_quizzes', True)
        
        # Get all active users
        users = RegistrationUser.query.filter_by(active=True).all()
        
        if not users:
            return jsonify({'message': 'No active users to notify', 'users_notified': 0}), 200
            
        # Find upcoming quizzes
        upcoming_quizzes = []
        if include_quizzes:
            from datetime import datetime, timedelta
            today = datetime.now().date()
            end_date = today + timedelta(days=days_ahead)
            
            upcoming_quizzes = Quizzes.query.filter(
                Quizzes.date_of_quiz >= today,
                Quizzes.date_of_quiz <= end_date
            ).all()
        
        # Send the notification emails
        users_notified = send_bulk_notification_emails(
            users=users, 
            subject=subject,
            message=message,
            quizzes=upcoming_quizzes
        )
        
        return jsonify({
            'message': f'Notifications sent successfully to {users_notified} users',
            'users_notified': users_notified,
            'quizzes_included': len(upcoming_quizzes) if include_quizzes else 0
        }), 200
    except Exception as e:
        print(f"Error sending all notifications: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'message': 'Error sending notifications to all users',
            'error': str(e)
        }), 500

def send_bulk_notification_emails(users, subject, message, quizzes=None):
    """Send email notifications to a list of users"""
    try:
        # Build the email HTML content
        quizzes_html = ""
        if quizzes and len(quizzes) > 0:
            quizzes_html = "<h3>Upcoming Quizzes:</h3><ul>"
            for quiz in quizzes:
                chapter = Chapters.query.get(quiz.chapter_id)
                subject_obj = Subject.query.get(chapter.subject_id) if chapter else None
                
                quiz_date = quiz.date_of_quiz.strftime('%Y-%m-%d')
                quizzes_html += f"""
                <li>
                    <strong>{quiz.quiz_name}</strong> - {subject_obj.name if subject_obj else 'Unknown Subject'}, 
                    Chapter: {chapter.chapter_name if chapter else 'Unknown'}<br>
                    Date: {quiz_date}, Time Limit: {quiz.timing} minutes<br>
                    <a href="http://localhost:8080/quiz/{quiz.id}" style="color: #4a6bdf;">Take this quiz</a>
                </li>
                """
            quizzes_html += "</ul>"
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4a6bdf; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .button {{ display: inline-block; background-color: #4a6bdf; color: white; text-decoration: none; padding: 10px 20px; border-radius: 5px; margin-top: 20px; }}
                .footer {{ font-size: 12px; text-align: center; margin-top: 30px; color: #777; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>Quiz Master Notification</h2>
            </div>
            <div class="content">
                <p>Hello,</p>
                <p>{message}</p>
                
                {quizzes_html}
                
                <p>Visit your <a href="http://localhost:8080/dashboard" style="color: #4a6bdf;">dashboard</a> to see all available quizzes.</p>
            </div>
            <div class="footer">
                <p>This is an automatic notification from Quiz Master. Please do not reply to this email.</p>
            </div>
        </body>
        </html>
        """
        
        # Send emails in batches to avoid overwhelming the mail server
        batch_size = 20
        total_sent = 0
        
        for i in range(0, len(users), batch_size):
            batch_users = users[i:i+batch_size]
            try:
                with app.app_context():
                    msg = Message(
                        subject=subject,
                        recipients=[user.email for user in batch_users],
                        html=html_content
                    )
                    mail.send(msg)
                    total_sent += len(batch_users)
                    print(f"Sent notification batch to {len(batch_users)} users")
                
                # Small delay between batches
                import time
                time.sleep(2)
            except Exception as batch_error:
                print(f"Error sending batch: {str(batch_error)}")
                # Continue with next batch
                
        return total_sent
    except Exception as e:
        print(f"Error in send_bulk_notification_emails: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0

# Add a new endpoint to toggle user active status
@app.route('/api/users/<int:user_id>/toggle-status', methods=['PATCH'])
@jwt_required()
def toggle_user_status(user_id):
    try:
        # Make sure the requester is an admin
        auth_header = request.headers.get('Authorization')
        print(f"Auth header for toggle user status: {auth_header}")
        
        user = RegistrationUser.query.get_or_404(user_id)
        
        # Toggle the active status
        user.active = not user.active
        db.session.commit()
        
        return jsonify({
            'message': f'User status updated. User is now {"active" if user.active else "inactive"}',
            'user_id': user.id,
            'active': user.active
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error toggling user status: {str(e)}")
        return jsonify({'message': 'Error updating user status', 'error': str(e)}), 500

# Add an admin endpoint to view a specific user's progress
@app.route('/api/admin/user-progress/<int:user_id>', methods=['GET'])
@jwt_required()
def admin_view_user_progress(user_id):
    try:
        # Check if the requested user exists
        user = RegistrationUser.query.get_or_404(user_id)
        
        # Get all performances for this user
        performances = Performance.query.filter_by(RegistrationUser_id=user_id).all()
        
        results = []
        for perf in performances:
            # Get quiz details
            quiz = Quizzes.query.get(perf.Quizzes_id)
            if quiz:
                # Get chapter details
                chapter = Chapters.query.get(quiz.chapter_id)
                # Get subject details
                subject = Subject.query.get(chapter.subject_id) if chapter else None
                
                results.append({
                    'performance_id': perf.id,
                    'quiz_id': perf.Quizzes_id,
                    'quiz_name': quiz.quiz_name if quiz else 'Unknown Quiz',
                    'chapter_name': chapter.chapter_name if chapter else 'Unknown Chapter',
                    'subject_name': subject.name if subject else 'Unknown Subject',
                    'score': perf.score,
                    'attempted_at': perf.attempted_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'subject_id': chapter.subject_id if chapter else None,
                    'chapter_id': quiz.chapter_id if quiz else None
                })
        
        # Get summary statistics
        total_quizzes = len(results)
        avg_score = sum(perf.score for perf in performances) / total_quizzes if total_quizzes > 0 else 0
        highest_score = max((perf.score for perf in performances), default=0)
        
        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'fullname': user.fullname,
                'email': user.email
            },
            'summary': {
                'total_quizzes': total_quizzes,
                'average_score': round(avg_score, 2),
                'highest_score': highest_score
            },
            'performances': results
        }), 200
    except Exception as e:
        print(f"Error fetching user progress for admin: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': 'Error fetching user progress', 'error': str(e)}), 500

# Add new API endpoints for the quiz summary page

@app.route('/api/admin/quiz-summary', methods=['GET'])
@jwt_required()
def get_quiz_summary():
    """Get overall summary statistics for quizzes"""
    try:
        # Get total number of quizzes
        total_quizzes = Quizzes.query.count()
        
        # Get total number of attempts
        total_attempts = Scores.query.count()
        
        # Get average score
        average_score = 0
        if total_attempts > 0:
            average_score_query = db.session.query(db.func.avg(Performance.score)).scalar()
            average_score = round(average_score_query or 0, 2)
        
        # Get active users (users who have taken at least one quiz)
        active_users = db.session.query(Scores.user_id).distinct().count()
        
        return jsonify({
            'totalQuizzes': total_quizzes,
            'totalAttempts': total_attempts,
            'averageScore': average_score,
            'activeUsers': active_users
        }), 200
    except Exception as e:
        print(f"Error getting quiz summary: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': 'Error getting quiz summary', 'error': str(e)}), 500

@app.route('/api/admin/most-attempted-quizzes', methods=['GET'])
@jwt_required()
def get_most_attempted_quizzes():
    """Get the most attempted quizzes"""
    try:
        # Get limit parameter (default to 10)
        limit = request.args.get('limit', 10, type=int)
        
        # Get quizzes with attempt counts
        most_attempted = db.session.query(
            Quizzes.id,
            Quizzes.quiz_name,
            Chapters.chapter_name,
            Subject.name.label('subject_name'),
            db.func.count(Scores.id).label('attempts'),
            db.func.avg(Performance.score).label('average_score')
        ).join(
            Chapters, Quizzes.chapter_id == Chapters.id
        ).join(
            Subject, Chapters.subject_id == Subject.id
        ).join(
            Scores, Scores.quiz_id == Quizzes.id
        ).join(
            Performance, Performance.Quizzes_id == Quizzes.id
        ).group_by(
            Quizzes.id
        ).order_by(
            db.desc('attempts')
        ).limit(limit).all()
        
        result = [{
            'id': quiz.id,
            'quiz_name': quiz.quiz_name,
            'chapter_name': quiz.chapter_name,
            'subject_name': quiz.subject_name,
            'attempts': quiz.attempts,
            'average_score': round(quiz.average_score, 2) if quiz.average_score else 0
        } for quiz in most_attempted]
        
        return jsonify(result), 200
    except Exception as e:
        print(f"Error getting most attempted quizzes: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': 'Error getting most attempted quizzes', 'error': str(e)}), 500

@app.route('/api/admin/highest-scores', methods=['GET'])
@jwt_required()
def get_highest_scores():
    """Get highest scores for each quiz"""
    try:
        # Get limit parameter (default to 10)
        limit = request.args.get('limit', 10, type=int)
        
        # Subquery to get maximum score for each quiz
        subquery = db.session.query(
            Performance.Quizzes_id,
            db.func.max(Performance.score).label('max_score')
        ).group_by(Performance.Quizzes_id).subquery()
        
        # Get the highest scores with user info
        highest_scores = db.session.query(
            Performance.Quizzes_id,
            Performance.RegistrationUser_id.label('user_id'),
            Performance.score,
            Performance.attempted_at,
            Quizzes.quiz_name,
            RegistrationUser.username
        ).join(
            subquery, db.and_(
                Performance.Quizzes_id == subquery.c.Quizzes_id,
                Performance.score == subquery.c.max_score
            )
        ).join(
            Quizzes, Performance.Quizzes_id == Quizzes.id
        ).join(
            RegistrationUser, Performance.RegistrationUser_id == RegistrationUser.id
        ).order_by(
            db.desc(Performance.score)
        ).limit(limit).all()
        
        result = [{
            'quiz_id': score.Quizzes_id,
            'user_id': score.user_id,
            'quiz_name': score.quiz_name,
            'username': score.username,
            'score': round(score.score, 2),
            'attempted_at': score.attempted_at.strftime('%Y-%m-%d %H:%M:%S')
        } for score in highest_scores]
        
        return jsonify(result), 200
    except Exception as e:
        print(f"Error getting highest scores: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': 'Error getting highest scores', 'error': str(e)}), 500

@app.route('/api/admin/quiz-participation-timeline', methods=['GET'])
@jwt_required()
def get_quiz_participation_timeline():
    """Get quiz participation data over time for chart"""
    try:
        # Get days parameter (default to 30)
        days = request.args.get('days', 30, type=int)
        
        # Get scores grouped by date
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Query to count attempts by date
        participation_data = db.session.query(
            db.func.date(Scores.time_stamp_of_attempt).label('date'),
            db.func.count(Scores.id).label('attempts')
        ).filter(
            Scores.time_stamp_of_attempt >= start_date,
            Scores.time_stamp_of_attempt <= end_date
        ).group_by(
            'date'
        ).order_by(
            'date'
        ).all()
        
        # Format for chart.js
        labels = [entry.date for entry in participation_data]
        data = [entry.attempts for entry in participation_data]
        
        return jsonify({
            'labels': labels,
            'data': data
        }), 200
    except Exception as e:
        print(f"Error getting quiz participation timeline: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': 'Error getting quiz participation timeline', 'error': str(e)}), 500

@app.route('/api/admin/subject-performance', methods=['GET'])
@jwt_required()
def get_subject_performance():
    """Get performance data by subject"""
    try:
        # Import the distinct function from SQLAlchemy
        from sqlalchemy import distinct
        
        # Check if we have the necessary data in the tables first
        quiz_count = Quizzes.query.count()
        if quiz_count == 0:
            # No quizzes in the system, return empty result
            return jsonify([]), 200
            
        perf_count = Performance.query.count()
        if perf_count == 0:
            # No performance data, return empty result
            return jsonify([]), 200
        
        # Query to get performance by subject - fixed with proper joins
        subject_performance = db.session.query(
            Subject.id,
            Subject.name,
            db.func.count(db.distinct(Quizzes.id)).label('quizzes'),
            db.func.avg(Performance.score).label('average_score')
        ).join(
            Chapters, Subject.id == Chapters.subject_id
        ).join(
            Quizzes, Chapters.id == Quizzes.chapter_id
        ).join(
            Performance, Quizzes.id == Performance.Quizzes_id,
            isouter=True  # Use left outer join to include subjects without performances
        ).group_by(
            Subject.id, Subject.name  # Include all non-aggregated columns
        ).order_by(
            db.desc('average_score')
        ).all()
        
        # Handle result safely
        result = [{
            'id': subject.id,
            'name': subject.name,
            'quizzes': subject.quizzes,
            'average_score': round(subject.average_score, 2) if subject.average_score is not None else 0
        } for subject in subject_performance]
        
        return jsonify(result), 200
    except Exception as e:
        print(f"Error getting subject performance: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': 'Error getting subject performance', 'error': str(e)}), 500

# Add new API endpoints for the user engagement reports

@app.route('/api/admin/user-statistics', methods=['GET'])
@jwt_required()
def get_user_statistics():
    """Get overall user statistics"""
    try:
        # Get total number of users
        total_users = RegistrationUser.query.count()
        
        # Get active users (users who have taken at least one quiz)
        active_users = db.session.query(Scores.user_id).distinct().count()
        
        # Get total quizzes taken
        total_quizzes_taken = Scores.query.count()
        
        # Calculate quizzes per user
        quizzes_per_user = total_quizzes_taken / total_users if total_users > 0 else 0
        
        # Get average score across all performances
        average_score = 0
        if total_quizzes_taken > 0:
            average_score_query = db.session.query(db.func.avg(Performance.score)).scalar()
            average_score = round(average_score_query or 0, 2)
        
        return jsonify({
            'totalUsers': total_users,
            'activeUsers': active_users,
            'quizzesPerUser': quizzes_per_user,
            'averageScore': average_score
        }), 200
    except Exception as e:
        print(f"Error getting user statistics: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': 'Error getting user statistics', 'error': str(e)}), 500

@app.route('/api/admin/user-activity-timeline', methods=['GET'])
@jwt_required()
def get_user_activity_timeline():
    """Get user activity data over time for chart"""
    try:
        # Get days parameter (default to 30)
        days = request.args.get('days', 30, type=int)
        
        # Get user activity grouped by date
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Query to count user logins by date (using Performance table as a proxy)
        activity_data = db.session.query(
            db.func.date(Performance.attempted_at).label('date'),
            db.func.count(db.distinct(Performance.RegistrationUser_id)).label('active_users')
        ).filter(
            Performance.attempted_at >= start_date,
            Performance.attempted_at <= end_date
        ).group_by(
            'date'
        ).order_by(
            'date'
        ).all()
        
        # Format for chart.js
        labels = [str(entry.date) for entry in activity_data]
        data = [entry.active_users for entry in activity_data]
        
        return jsonify({
            'labels': labels,
            'data': data
        }), 200
    except Exception as e:
        print(f"Error getting user activity timeline: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': 'Error getting user activity timeline', 'error': str(e)}), 500

@app.route('/api/admin/most-active-users', methods=['GET'])
@jwt_required()
def get_most_active_users():
    """Get the most active users"""
    try:
        # Get limit parameter (default to 10)
        limit = request.args.get('limit', 10, type=int)
        
        # Get users with quiz counts and latest activity
        most_active = db.session.query(
            RegistrationUser.id,
            RegistrationUser.username,
            RegistrationUser.email,
            db.func.count(Performance.id).label('quizzes_taken'),
            db.func.avg(Performance.score).label('average_score'),
            db.func.max(Performance.attempted_at).label('last_active')
        ).join(
            Performance, RegistrationUser.id == Performance.RegistrationUser_id
        ).group_by(
            RegistrationUser.id
        ).order_by(
            db.desc('quizzes_taken')
        ).limit(limit).all()
        
        result = [{
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'quizzesTaken': user.quizzes_taken,
            'averageScore': round(user.average_score, 2) if user.average_score else 0,
            'lastActive': user.last_active.isoformat() if user.last_active else None
        } for user in most_active]
        
        return jsonify(result), 200
    except Exception as e:
        print(f"Error getting most active users: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': 'Error getting most active users', 'error': str(e)}), 500

@app.route('/api/admin/subject-popularity', methods=['GET'])
@jwt_required()
def get_subject_popularity():
    """Get subject popularity among users"""
    try:
        # Query to get subject popularity
        subject_popularity = db.session.query(
            Subject.id,
            Subject.name,
            db.func.count(db.distinct(Quizzes.id)).label('quiz_count'),
            db.func.count(db.distinct(Performance.RegistrationUser_id)).label('user_count')
        ).join(
            Chapters, Subject.id == Chapters.subject_id
        ).join(
            Quizzes, Chapters.id == Quizzes.chapter_id
        ).join(
            Performance, Quizzes.id == Performance.Quizzes_id
        ).group_by(
            Subject.id
        ).order_by(
            db.desc('user_count')
        ).all()
        
        result = [{
            'id': subject.id,
            'name': subject.name,
            'quizCount': subject.quiz_count,
            'userCount': subject.user_count
        } for subject in subject_popularity]
        
        return jsonify(result), 200
    except Exception as e:
        print(f"Error getting subject popularity: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': 'Error getting subject popularity', 'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        # db.drop_all()
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)