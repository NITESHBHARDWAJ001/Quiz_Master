from celery import Celery
from datetime import datetime
from celery.schedules import crontab
import pytz

def make_celery(app_name):
    """
    Create a Celery instance with common configuration
    """
    celery = Celery(
        app_name,
        broker='redis://localhost:6379/0',
        backend='redis://localhost:6379/0',
        include=['app']  # Include the app module to find tasks
    )
    
    # Configure Celery
    celery.conf.update(
        result_expires=3600,  # Results expire after 1 hour
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
    )
    
    # Add periodic tasks
    celery.conf.beat_schedule = {
        'send-monthly-performance-reports': {
            'task': 'celery_worker.send_monthly_reports',
            # Run at 2:00 AM on the 1st of every month
            'schedule': crontab(minute=0, hour=2, day_of_month=1),
            'args': (None, None),  # Will use current month/year
        },
    }
    
    return celery

# Initialize Celery
celery = make_celery('quiz_master')

@celery.task(name="celery_worker.process_login")
def process_login(user_id, timestamp):
    """
    Process a user login event. This is just a sample task.
    In a real app, you might do things like:
    - Update last login timestamp
    - Record login for analytics
    - Check for suspicious activity
    """
    print(f"Processing login for user {user_id} at {timestamp}")
    
    # Simulate some work
    import time
    time.sleep(1)
    
    # Record the login in a database or logging system
    # (Just printing for now)
    print(f"Recorded login for user {user_id}")
    
    return {
        "user_id": user_id,
        "processed_at": datetime.utcnow().isoformat(),
        "status": "success"
    }

@celery.task(name="celery_worker.send_quiz_notification", bind=True, max_retries=3)
def send_quiz_notification(self, quiz_id):
    """
    Send notifications to all users about a new quiz.
    This task has retry capability to handle temporary failures.
    """
    try:
        print(f"[CELERY] Starting quiz notification task for quiz ID {quiz_id}")
        
        # Import the function from app.py
        from app import send_quiz_notification_emails, app
        
        # Use app context to ensure database connections work correctly
        with app.app_context():
            # Send the notifications
            success = send_quiz_notification_emails(quiz_id)
            
            if not success:
                # If not successful, retry the task
                print(f"[CELERY] Failed to send notifications for quiz {quiz_id}, scheduling retry")
                raise self.retry(countdown=300)  # Retry after 5 minutes
            
            print(f"[CELERY] Successfully sent notifications for quiz {quiz_id}")
            
            # Return task result
            return {
                "quiz_id": quiz_id,
                "processed_at": datetime.utcnow().isoformat(),
                "success": True,
                "message": "Notifications sent successfully"
            }
    except Exception as e:
        print(f"[CELERY] Error in quiz notification task: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # For serious errors, try to retry the task
        try:
            if self.request.retries < self.max_retries:
                print(f"[CELERY] Retrying notification task for quiz {quiz_id} (attempt {self.request.retries + 1})")
                raise self.retry(countdown=300 * (self.request.retries + 1))  # Increasing backoff
        except Exception as retry_error:
            print(f"[CELERY] Failed to schedule retry: {str(retry_error)}")
        
        return {
            "quiz_id": quiz_id,
            "processed_at": datetime.utcnow().isoformat(),
            "success": False,
            "error": str(e)
        }

@celery.task(name="celery_worker.send_monthly_reports")
def send_monthly_reports(month=None, year=None):
    """Send monthly performance reports to all users"""
    try:
        print(f"Starting monthly report task for {month}/{year}")
        
        # If month/year not specified, use previous month
        if not month or not year:
            from datetime import datetime, timedelta
            # Get first day of current month
            today = datetime.today()
            first_day = datetime(today.year, today.month, 1)
            # Go back one day to get the last day of previous month
            last_month = first_day - timedelta(days=1)
            month = last_month.month
            year = last_month.year
        
        # Import required modules from app.py
        from app import generate_performance_report_html, generate_performance_report_pdf, RegistrationUser, mail, Message
        from flask import current_app
        
        # Get all active users
        with current_app.app_context():
            users = RegistrationUser.query.filter_by(active=True).all()
            
            if not users:
                print("No active users to send reports to")
                return {"status": "success", "message": "No active users to send reports to"}
            
            # Get month name
            import calendar
            month_name = calendar.month_name[month]
            
            # Send reports in batches
            batch_size = 10
            successful_sends = 0
            failed_sends = 0
            
            for i in range(0, len(users), batch_size):
                batch_users = users[i:i+batch_size]
                
                for user in batch_users:
                    try:
                        # Generate PDF report for this user
                        pdf_data = generate_performance_report_pdf(user.id, month, year)
                        
                        if not pdf_data:
                            print(f"No data for user {user.id} in {month_name} {year}")
                            continue
                        
                        # Create email
                        msg = Message(
                            subject=f"Quiz Master Monthly Performance Report - {month_name} {year}",
                            recipients=[user.email],
                            body=f"Please find attached your performance report for {month_name} {year}.",
                            html=f"""
                            <html>
                            <body>
                                <h2>Your Monthly Performance Report</h2>
                                <p>Hello {user.fullname},</p>
                                <p>Please find attached your Quiz Master performance report for {month_name} {year}.</p>
                                <p>This report includes a summary of your quiz activities, scores, and comparisons with other students.</p>
                                <p>Thank you for using Quiz Master!</p>
                            </body>
                            </html>
                            """
                        )
                        
                        # Attach PDF
                        msg.attach(
                            filename=f"performance_report_{month_name}_{year}.pdf",
                            content_type="application/pdf",
                            data=pdf_data
                        )
                        
                        # Send email
                        mail.send(msg)
                        successful_sends += 1
                        
                    except Exception as e:
                        print(f"Error sending monthly report to user {user.id}: {str(e)}")
                        failed_sends += 1
                
                # Small delay between batches
                import time
                time.sleep(5)
            
            print(f"Monthly reports task completed. Success: {successful_sends}, Failed: {failed_sends}")
            return {
                "status": "success",
                "month": month,
                "year": year,
                "successful_sends": successful_sends,
                "failed_sends": failed_sends
            }
            
    except Exception as e:
        print(f"Error in monthly reports task: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "month": month,
            "year": year,
            "error": str(e)
        }

if __name__ == '__main__':
    print("Starting Celery worker")
    celery.start()