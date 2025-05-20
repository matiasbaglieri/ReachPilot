class LinkedinService:
    def execute(self, user):
        print(f"Executing Linkedin service with:")
        print(f"Email: {user['email']}")
        print(f"Password: {user['password']}")