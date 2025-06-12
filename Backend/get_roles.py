from app.database import Database
from app.models.Admin import Admin
from app.models.Rider import Rider
from app.models.Driver import Driver

db = Database.get_db()

def get_user_collection_by_role(role: str):
        if role == "driver":
            return Driver
        elif role == "rider":
            return Rider
        elif(role == "admin"):
            return Admin