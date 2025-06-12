from datetime import datetime, timezone
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import Database

rider_collection = Database.get_db().rider


class Rider:
    def __init__(
        self,
        username,
        email,
        city,
        state,
        ssn,
        phone_number = None,
        password=None,
        _id=None,
        created_at=None,
        updated_at = None,
        password_hash=None,
        profile_image_id = None
    ):
        self._id = ObjectId(_id) if _id else ObjectId()
        self.username = username
        self.email = email
        self.phone_number = phone_number
        self.ssn = ssn
        self.state = state
        self.city = city
        self.profile_image_id = profile_image_id

        # Handle password and password_hash initialization
        if password and not password_hash:
            self.password_hash = generate_password_hash(password)
        else:
            self.password_hash = password_hash

        # Handle timestamps
        self.created_at = created_at if created_at else datetime.now(timezone.utc)
        self.updated_at = updated_at if updated_at else datetime.now(timezone.utc)

    @staticmethod
    def get_by_id(user_id):
        try:
            user_data = rider_collection.find_one({"_id": ObjectId(user_id)})
            return Rider.from_db(user_data) if user_data else None
        except Exception as e:
            print(f"Error fetching Rider by ID: {e}")
            return None

    @staticmethod
    def get_by_email(email: str):
        try:
            user_data = rider_collection.find_one({"email": email})
            return Rider.from_db(user_data) if user_data else None
        except Exception as e:
            print(f"Error fetching Rider by Email: {e}")
            return None

    @staticmethod
    def from_db(user_data):
        if not user_data:
            return None
        return Rider(
            username=user_data["username"],
            email=user_data["email"],
            phone_number=user_data["phone_number"],
            _id=user_data["_id"],
            password_hash=user_data["password_hash"],
            created_at=user_data["created_at"],
            updated_at=user_data["updated_at"],
            city=user_data.get("city"),
            ssn = user_data.get("ssn"),
            state=user_data.get("state"),
            profile_image_id=user_data.get("profile_image_id")
        )

    def save(self):
        user_data = {
            "_id": self._id,
            "username": self.username,
            "email": self.email,
            "password_hash": self.password_hash,
            "created_at": self.created_at,
            "updated_at": datetime.now(timezone.utc),
            "phone_number": self.phone_number,
            "ssn": self.ssn,
            "city": self.city,
            "state": self.state,
            "profile_image_id": self.profile_image_id
        }
        rider_collection.update_one({"_id": self._id}, {"$set": user_data}, upsert=True)
        return self

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
            "role": "rider",
            "city":self.city,
            "state": self.state,
            "ssn":self.ssn,
            "profile_image_id": self.profile_image_id
        }

    def __repr__(self):
        return f"<Rider {self.username} ({self.email})>"

    def update_details(self, data):
        update_data = {
            "username": data.get("username"),
            "email": data.get("email"),
            "phone_number": data.get("phone_number"),
            "updated_at": datetime.now(timezone.utc),
            "city": data.get("city"),
            "state": data.get("state"),
            "ssn": data.get("ssn"),
        }
        if update_data:
            result = rider_collection.update_one({"_id": self._id}, {"$set": update_data}, upsert=True)
            if result.modified_count == 0:
                raise Exception("Rider details not updated")
            return True
