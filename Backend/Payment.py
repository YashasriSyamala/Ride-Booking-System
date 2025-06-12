from datetime import datetime, timezone
from app.database import Database
from bson import ObjectId

payment_collection = Database.get_db().payment


class Payment:
    def __init__(
        self,
        rider_id,
        payment_method=None,
        payment_status=None,
        payment_date=None,
        _id=None,
    ) -> None:
        self._id = ObjectId(_id) if _id else ObjectId()
        self.rider_id = ObjectId(rider_id)
        self.payment_method = payment_method
        self.payment_status = payment_status
        self.payment_date = payment_date if payment_date else datetime.now(timezone.utc)
    
    @staticmethod
    def get_by_id(payment_id):
        try:
            user_data = payment_collection.find_one({"_id": ObjectId(payment_id)})
            return Payment.from_db(user_data) if user_data else None
        except Exception as e:
            print(f"Error fetching Payment by ID: {e}")
            return None

    @staticmethod
    def from_db(data):
        if not data:
            return None
        return Payment(
            _id=data["_id"],
            rider_id=data["rider_id"],
            payment_status=data["payment_status"],
            payment_date=data["payment_date"],
            payment_method=data["payment_method"]
        )

    def to_dict(self):
        return{
            "_id": str(self._id),
            "rider_id": str(self.rider_id),
            "payment_status": self.payment_status,
            "payment_date": self.payment_date.isoformat(),
            "payment_method": self.payment_method
        }

    def save(self):
        payment_data = {
            "_id": self._id,
            "rider_id": self.rider_id,
            "payment_method": self.payment_method,
            "payment_status": self.payment_status,
            "payment_date": self.payment_date,
        }
        payment_collection.update_one(
            {"_id": self._id}, {"$set": payment_data}, upsert=True
        )
        return self._id

    def make_payment(self):
        payment_data = {
            "_id": self._id,
            "rider_id": self.rider_id,
            "payment_method": self.payment_method,
            "payment_status": self.payment_status,
            "payment_date": self.payment_date,
        }
        payment_collection.update_one(
            {"_id": self._id}, {"$set": payment_data}, upsert=True
        )
        return self._id
