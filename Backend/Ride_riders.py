
from bson import ObjectId
from app.database import Database
rides_rider_collection = Database.get_db().rides_rider


class Rides_rider:
    def __init__(
        self,
        rider_id,
        ride_id,
        status,
        _id=None,
    ):
        self._id = ObjectId(_id) if _id else ObjectId()
        self.rider_id = rider_id
        self.ride_id = ride_id
        self.status = status

    @staticmethod
    def get_by_id(_id):
        try:
            user_data = rides_rider_collection.find_one({"_id": ObjectId(_id)})
            return Rides_rider.from_db(user_data) if user_data else None
        except Exception as e:
            print(f"Error fetching rides_rider by ID: {e}")
            return None
    @staticmethod
    def get_by_ride_id(ride_id):
        try:
            user_data = rides_rider_collection.find_one({"ride_id": ObjectId(ride_id)})
            return Rides_rider.from_db(user_data) if user_data else None
        except Exception as e:
            print(f"Error fetching rides_rider by ID: {e}")
            return None

    @staticmethod
    def from_db(user_data):
        if not user_data:
            return None
        return Rides_rider(
            _id = user_data.get("_id"),
            ride_id=str(user_data.get("ride_id")),
            status=user_data.get("status"),
            rider_id=str(user_data.get("rider_id"))
        )

    def save(self):
        user_data = {
            "_id": self._id,
            "status": self.status,
            "rider_id": ObjectId(self.rider_id),
            "ride_id": ObjectId(self.ride_id)
        }
        rides_rider_collection.update_one({"_id": self._id}, {"$set": user_data}, upsert=True)
        return self

    @staticmethod
    def get_rides_by_status_and_rider_id(rider_id, status):

        condition1 = {"rider_id": ObjectId(rider_id)}
        condition2 = {"status": status}

        cursor = rides_rider_collection.find({"$and": [condition1, condition2]})
        return [Rides_rider.from_db(ride) for ride in cursor]
