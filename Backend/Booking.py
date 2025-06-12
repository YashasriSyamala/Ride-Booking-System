from app.database import Database
from bson import ObjectId
from datetime import datetime, timezone

booking_collection = Database.get_db().booking


class Booking:
    def __init__(
        self,
        driver_id,
        ride_id,
        rider_id,
        payment_id,
        rider_pickup_location,
        driver_earning=0,
        admin_commission=0,
        created_at=None,
        updated_at=None,
        _id=None,
    ) -> None:
        self._id = ObjectId(_id) if _id else ObjectId()
        self.driver_id = ObjectId(driver_id)
        self.ride_id = ObjectId(ride_id)
        self.rider_id = ObjectId(rider_id)
        self.driver_earning = driver_earning
        self.admin_commission = admin_commission
        self.payment_id = payment_id
        self.rider_pickup_location = rider_pickup_location

        self.created_at = created_at if created_at else datetime.now(timezone.utc)

    def add_booking(self, price_per_seat):
        booking_data = {
            "booking_id": self._id,
            "driver_id": self.driver_id,
            "ride_id": self.ride_id,
            "rider_id": self.rider_id,
            "rider_pickup_location": self.rider_pickup_location,
            "driver_earning": (price_per_seat * 0.8),
            "admin_commission": (price_per_seat * 0.2),
            "payment_id": self.payment_id,
            "created_at": self.created_at,
        }
        result = booking_collection.update_one(
            {"_id": self._id}, {"$set": booking_data}, upsert=True
        )
        return result.modified_count

    def save(self):
        booking_data = {
            "booking_id": self._id,
            "driver_id": self.driver_id,
            "ride_id": self.ride_id,
            "rider_id": self.rider_id,
            "rider_pickup_location": self.rider_pickup_location,
            "driver_earning": self.driver_earning,
            "admin_commission": self.admin_commission,
            "payment_id": self.payment_id,
            "created_at": self.created_at,
        }
        result = booking_collection.update_one(
            {"_id": self._id}, {"$set": booking_data}, upsert=True
        )
        return result.modified_count

    @staticmethod
    def from_db(data):
        if not data:
            return None
        return Booking(
            _id=data["_id"],
            driver_id=data["driver_id"],
            ride_id=data["ride_id"],
            rider_id=data["rider_id"],
            rider_pickup_location=data["rider_pickup_location"],
            driver_earning=data["driver_earning"],
            admin_commission=data["admin_commission"],
            payment_id=data["payment_id"],
            created_at=data["created_at"],
        )

    def to_dict(self):
        return {
            "booking_id": str(self._id),
            "driver_id": str(self.driver_id),
            "ride_id": str(self.ride_id),
            "rider_pickup_location": self.rider_pickup_location,
            "driver_earning": self.driver_earning,
            "admin_commission": self.admin_commission,
            "payment_id": str(self.payment_id),
            "rider_id": str(self.rider_id),
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }

    @staticmethod
    def get_all_bookings_by_ride_id(ride_id):
        bookings_cursor = booking_collection.find({"ride_id": ObjectId(ride_id)})
        bookings = [Booking.from_db(booking) for booking in bookings_cursor]
        return bookings

    @staticmethod
    def get_booking_by_rider_for_ride(rider_id, ride_id):
        condition1 = {"ride_id": ObjectId(ride_id)}
        condition2 = {"rider_id": ObjectId(rider_id)}
        booking_cursor = booking_collection.find_one({"$and": [condition1, condition2]})
        booking = Booking.from_db(booking_cursor)
        return booking

    def calculate_driver_earnings_for_a_ride(ride_id):
        match_stage = {}

        # Add ride ID to the match stage if provided
        if ride_id:
            match_stage["ride_id"] = ObjectId(ride_id)

        # Aggregation pipeline
        pipeline = [
            {"$match": match_stage},  # Filter documents
            {"$group": {
                "_id": None,  # Group all matching documents
                "total_earnings": {"$sum": "$driver_earning"}  # Sum driver earnings
            }}
        ]

        result = booking_collection.aggregate(pipeline)
        total = next(result, {"total_earnings": 0})[
            "total_earnings"
        ]  # Get sum or default to 0
        return total

    def calculate_driver_earnings( driver_id=None):
        match_stage = {"driver_id": ObjectId(driver_id)}

        pipeline = [
            {"$match": match_stage},  # Filter documents
            {"$group": {
                "_id": None,  # Group all matching documents
                "total_earnings": {"$sum": "$driver_earning"}  # Sum driver earnings
            }}
        ]

        result = booking_collection.aggregate(pipeline)
        total = next(result, {"total_earnings": 0})[
            "total_earnings"
        ]  # Get sum or default to 0
        return total

    def calculate_admin_earnings(ride_id=None):
        match_stage = {}
        # Add ride ID to the match stage if provided
        if ride_id:
            match_stage["ride_id"] = ObjectId(ride_id)

        # Aggregation pipeline
        pipeline = [
            {"$match": match_stage},  # Filter documents
            {"$group": {
                "_id": None,  # Group all matching documents
                "total_earnings": {"$sum": "$admin_commission"}  # Sum driver earnings
            }}
        ]

        result = booking_collection.aggregate(pipeline)
        total = next(result, {"total_earnings": 0})[
            "total_earnings"
        ]  # Get sum or default to 0
        return total