# Quiz Master

A comprehensive quiz application for educational institutions, allowing administrators to create subjects, chapters, and quizzes, while students can take quizzes and track their progress.

## Features

### Administrator Features
- **Dashboard**: Overview of system statistics and user activity
- **Content Management**: Create and manage subjects, chapters, and quizzes
- **Question Bank**: Add and edit questions with multiple-choice options
- **User Management**: View and manage user accounts, activate/deactivate users
- **Analytics**: View detailed reports on quiz performance and user engagement
- **Notifications**: Send email notifications to users about new quizzes

### Student Features
- **Dashboard**: View available quizzes and recent activity
- **Quiz Taking**: Take quizzes with timed sessions
- **Progress Tracking**: View performance history and statistics
- **Performance Reports**: Download or email detailed performance reports
- **Search**: Find quizzes by subject, chapter, or keywords

## Tech Stack

### Frontend
- Vue.js 3 with Vue Router
- Bootstrap 5 for styling
- Chart.js for data visualization
- Axios for API communication

### Backend
- Flask (Python web framework)
- SQLAlchemy ORM with SQLite database
- JWT for authentication
- Celery for background tasks and scheduled jobs
- Redis for task queue and caching
- Flask-Mail for email notifications

## Installation

### Prerequisites
- Python 3.8 or higher
- Node.js 14 or higher
- Redis server (for Celery tasks)

### Backend Setup
1. Clone the repository
   ```
   git clone https://github.com/yourusername/quiz-master.git
   cd quiz-master
   ```

2. Create and activate a virtual environment
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install Python dependencies
   ```
   pip install -r requirements.txt
   ```

4. Initialize the database
   ```
   cd demo_b
   python app.py
   ```

5. Start the Celery worker (in a new terminal window)
   ```
   cd demo_b
   celery -A celery_worker worker --loglevel=info
   ```

6. Start the Flask server
   ```
   python app.py
   ```

### Frontend Setup
1. Navigate to the frontend directory
   ```
   cd demo
   ```

2. Install dependencies
   ```
   npm install
   ```

3. Start the development server
   ```
   npm run serve
   ```

4. Access the application at `http://localhost:8080`

## Project Structure

```
Quiz Master/
├── demo/                  # Frontend Vue.js application
│   ├── public/            # Static assets
│   ├── src/               # Source code
│   │   ├── assets/        # Images and other assets
│   │   ├── components/    # Vue components
│   │   ├── router/        # Vue Router configuration
│   │   ├── services/      # API services
│   │   ├── views/         # Page components
│   │   ├── App.vue        # Root component
│   │   └── main.js        # Application entry point
│   └── package.json       # Frontend dependencies
│
├── demo_b/                # Backend Flask application
│   ├── app.py             # Main application file
│   ├── celery_worker.py   # Celery configuration and tasks
│   ├── quiz2.db           # SQLite database
│   └── requirements.txt   # Backend dependencies
│
└── README.md              # Project documentation
```

## Using the Application

### Admin Access
1. Login with username `admin` and password `admin`
2. From the admin dashboard, you can:
   - Create and manage subjects, chapters, and quizzes
   - View and manage user accounts
   - View analytics and generate reports
   - Send notifications to users

### Student Access
1. Register a new account or login with existing credentials
2. From the student dashboard, you can:
   - Browse available quizzes by subject or chapter
   - Take quizzes and see your score immediately
   - View your progress and performance statistics
   - Download or email performance reports

## API Documentation

### Authentication Endpoints
- `POST /api/register`: Register a new user
- `POST /api/login`: Login and get JWT token

### Subject Endpoints
- `GET /api/subjects`: List all subjects
- `POST /api/admin/subjects`: Create a new subject
- `GET /api/subjects/<id>`: Get a specific subject
- `PUT /api/subjects/<id>`: Update a subject
- `DELETE /api/subjects/<id>`: Delete a subject

### Chapter Endpoints
- `GET /api/subjects/<id>/chapters`: List chapters for a subject
- `POST /api/subjects/<id>/chapters`: Add a chapter to a subject
- `GET /api/chapters/<id>`: Get a specific chapter
- `PUT /api/chapters/<id>`: Update a chapter
- `DELETE /api/chapters/<id>`: Delete a chapter

### Quiz Endpoints
- `GET /api/chapters/<id>/quizzes`: List quizzes for a chapter
- `POST /api/chapters/<id>/quizzes`: Add a quiz to a chapter
- `GET /api/quizzes/<id>`: Get a specific quiz
- `GET /api/quizzes/<id>/questions`: Get questions for a quiz
- `POST /api/quizzes/<id>/questions`: Add a question to a quiz
- `POST /api/submit-quiz`: Submit a completed quiz

### User Endpoints
- `GET /api/admin/users`: List all users (admin only)
- `PATCH /api/users/<id>/toggle-status`: Activate/deactivate a user
- `GET /api/user-progress/<id>`: Get a user's progress
- `GET /api/user/<id>/recent-scores`: Get a user's recent scores

### Analytics Endpoints
- `GET /api/admin/quiz-summary`: Get quiz performance summary
- `GET /api/admin/most-attempted-quizzes`: List most attempted quizzes
- `GET /api/admin/highest-scores`: List highest scores by quiz
- `GET /api/admin/subject-performance`: Get performance by subject
- `GET /api/admin/user-statistics`: Get user statistics
- `GET /api/admin/most-active-users`: List most active users

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
