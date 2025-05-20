from models.base import SessionLocal, User

class UserService:
    def execute(self, email, passwd, mailgun_api):
        session = SessionLocal()
        try:
            user = session.query(User).filter(User.email == email).first()
            if user is None:
                user = User(email=email, password=passwd, mailgun=mailgun_api)
                session.add(user)
                print(f"Inserted new user: {email}")
            else:
                user.password = passwd
                user.mailgun = mailgun_api
                print(f"Updated user: {email}")
            session.commit()
            # Return a dictionary with user data
            return {
                "id": user.id,
                "email": user.email,
                "password": user.password,
                "mailgun": user.mailgun
            }
        except Exception as e:
            session.rollback()
            print(f"Error: {e}")
        finally:
            session.close()