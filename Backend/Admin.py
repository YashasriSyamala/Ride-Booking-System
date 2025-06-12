from datetime import datetime, timezone
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import Database

admin_collection = Database.get_db().admin


class Admin:
    def __init__(
        self,
        username,
        email,
        phone_number=None,
        password=None,
        _id=None,
        created_at=None,
        updated_at=None,
        password_hash=None,
    ):
        self._id = ObjectId(_id) if _id else ObjectId()
        self.username = username
        self.email = email
        self.phone_number = phone_number

        # Handle password and password_hash initialization
        if password and not password_hash:
            self.password_hash = generate_password_hash(password)
        else:
            self.password_hash = password_hash

        self.created_at = created_at if created_at else datetime.now(timezone.utc)
        self.updated_at = updated_at if updated_at else datetime.now(timezone.utc)

    @staticmethod
    def get_by_id(user_id):
        try:
            user_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
            user_data = admin_collection.find_one({"_id": user_id})
            return Admin.from_db(user_data) if user_data else None
        except Exception as e:
            print(f"Error fetching admin by ID: {e}")
            return None

    @staticmethod
    def get_by_email(email):
        try:
            user_data = admin_collection.find_one({"email": email})
            return Admin.from_db(user_data) if user_data else None
        except Exception as e:
            print(f"Error fetching admin by email: {e}")
            return None

    @staticmethod
    def from_db(user_data):
        if not user_data:
            return None
        return Admin(
            _id=user_data.get("_id"),
            username=user_data.get("username"),
            email=user_data.get("email"),
            phone_number=user_data.get("phone_number"),
            password_hash=user_data.get("password_hash"),
            created_at=user_data.get("created_at"),
            updated_at=user_data.get("updated_at"),
        )

    def save(self):
        try:
            user_data = {
                "_id": self._id,
                "username": self.username,
                "email": self.email,
                "phone_number": self.phone_number,
                "password_hash": self.password_hash,
                "created_at": self.created_at,
                "updated_at": datetime.now(timezone.utc),
            }

            admin_collection.update_one(
                {"_id": self._id}, {"$set": user_data}, upsert=True
            )
            return self
        except Exception as e:
            print(f"Error saving admin: {e}")
            raise

    def check_password(self, password):
        if not password or not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": str(self._id),
            "username": self.username,
            "email": self.email,
            "phone_number": self.phone_number,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "role": "admin",
        }

    def __repr__(self):
        return f"<Admin {self.username} ({self.email})>"
    
    def update_details(self, data):
        update_data = {
            "username": data.get("username"),
            "email": data.get("email"),
            "phone_number": data.get("phone_number"),
            "updated_at": datetime.now(timezone.utc)
        }
        if update_data:
            result = admin_collection.update_one({"_id": self._id}, {"$set": update_data}, upsert=True)
            if result.modified_count == 0:
                raise Exception("Admin details not updated")
            return True
