from app import db, Role, RegistrationUser, Subject, Chapters, Quizzes, Questions, Scores, Performance
from werkzeug.security import generate_password_hash
from datetime import datetime

def seed_data():
    # Drop all tables and recreate them
    db.drop_all()
    db.create_all()

    # Seed Roles
    admin_role = Role(name="admin", description="Administrator role")
    user_role = Role(name="user", description="Regular user role")
    db.session.add_all([admin_role, user_role])
    db.session.commit()  # Commit roles first

    # Seed Users
    admin_user = RegistrationUser(
        fullname="Admin User",
        username="admin",
        email="admin@example.com",
        password=generate_password_hash("admin123"),
        qualification="Masters",
        self_description="Administrator of the system",
        fs_uniquifier=generate_password_hash("admin@example.com"),
        active=True,
        roles=[admin_role]
    )
    regular_user = RegistrationUser(
        fullname="John Doe",
        username="johndoe",
        email="johndoe@example.com",
        password=generate_password_hash("password123"),
        qualification="Bachelors",
        self_description="A regular user",
        fs_uniquifier=generate_password_hash("johndoe@example.com"),
        active=True,
        roles=[user_role]
    )
    db.session.add_all([admin_user, regular_user])
    db.session.commit()  # Commit users after roles

    # Seed Subjects
    math_subject = Subject(name="Mathematics", description="Study of numbers and shapes")
    science_subject = Subject(name="Science", description="Study of the natural world")
    db.session.add_all([math_subject, science_subject])
    db.session.commit()  # Commit subjects

    # Seed Chapters
    algebra_chapter = Chapters(subject_id=math_subject.id, chapter_name="Algebra", description="Introduction to Algebra")
    physics_chapter = Chapters(subject_id=science_subject.id, chapter_name="Physics", description="Introduction to Physics")
    db.session.add_all([algebra_chapter, physics_chapter])
    db.session.commit()  # Commit chapters

    # Seed Quizzes
    algebra_quiz = Quizzes(
        chapter_id=algebra_chapter.id,
        quiz_name="Algebra Basics",
        date_of_quiz=datetime(2025, 3, 25),
        timing=30
    )
    physics_quiz = Quizzes(
        chapter_id=physics_chapter.id,
        quiz_name="Physics Basics",
        date_of_quiz=datetime(2025, 3, 26),
        timing=40
    )
    db.session.add_all([algebra_quiz, physics_quiz])
    db.session.commit()  # Commit quizzes

    # Seed Questions
    algebra_question = Questions(
        quiz_id=algebra_quiz.id,
        question_statement="What is 2 + 2?",
        option1="3",
        option2="4",
        option3="5",
        option4="6",
        marks=5
    )
    physics_question = Questions(
        quiz_id=physics_quiz.id,
        question_statement="What is the speed of light?",
        option1="300,000 km/s",
        option2="150,000 km/s",
        option3="450,000 km/s",
        option4="600,000 km/s",
        marks=10
    )
    db.session.add_all([algebra_question, physics_question])
    db.session.commit()  # Commit questions

    # Seed Scores
    algebra_score = Scores(
        quiz_id=algebra_quiz.id,
        user_id=regular_user.id,
        total_scored=5
    )
    physics_score = Scores(
        quiz_id=physics_quiz.id,
        user_id=regular_user.id,
        total_scored=10
    )
    db.session.add_all([algebra_score, physics_score])
    db.session.commit()  # Commit scores

    # Seed Performance
    algebra_performance = Performance(
        user_id=regular_user.id,
        quiz_id=algebra_quiz.id,
        score=5.0,
        attempted_at=datetime.utcnow()
    )
    physics_performance = Performance(
        user_id=regular_user.id,
        quiz_id=physics_quiz.id,
        score=10.0,
        attempted_at=datetime.utcnow()
    )
    db.session.add_all([algebra_performance, physics_performance])
    db.session.commit()  # Commit performance

    print("Database seeded successfully!")

if __name__ == "__main__":
    seed_data()
