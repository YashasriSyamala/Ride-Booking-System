
from app.database import Database
reset_password = Database.get_db().reset_password


class Reset_password:
    def __init__(
        self,
        role,
        email,
        token,
        token_expiry
    ):
        self.token = token
        self.token_expiry = token_expiry,
        self.email = email,
        self.role = role


    @staticmethod
    def from_db(user_data):
        if not user_data:
            return None
        return Reset_password(
            token = user_data.get("token"),
            token_expiry=user_data.get("token_expiry"),
            email=user_data.get("email"),
            role = user_data.get("role")
        )
    
    @staticmethod
    def find_token(token):
        cursor = reset_password.find_one({"token": token})
        return Reset_password.from_db(cursor) if cursor else None

    def save(self):
        user_data = {
            "token": self.token,
            "token_expiry": self.token_expiry,
            "email": self.email,
            "role": self.role,
        }
        reset_password.update_one({"token": self.token}, {"$set": user_data}, upsert=True)
        return self