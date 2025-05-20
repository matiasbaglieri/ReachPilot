from models.base import SessionLocal, User

class EmailService:
    def execute(self, user):
        print(f"Executing Email service with:")
        print(f"Email: {user['email']}")
        print(f"Mailgun API: {user['mailgun']}")