from app.database import Database
from bson import ObjectId
from datetime import datetime, timezone


refund_collection = Database.get_db().refund


class Refund:
    def __init__(
        self, booking_id, rider_id, amount_refunded, refund_status, payment_id, _id=None
    ) -> None:
        self._id = ObjectId(_id) if _id else ObjectId()
        self.booking_id = booking_id
        self.rider_id = rider_id
        self.amount_refunded = amount_refunded
        self.refund_status = refund_status
        self.payment_id = payment_id
        self.refund_date = datetime.now(timezone.utc)

    def save(self):
        refund_data = {
            "booking_id": self.booking_id,
            "rider_id": self.rider_id,
            "amount_refunded": self.amount_refunded,
            "refund_status": self.refund_status,
            "payment_id": self.payment_id,
            "refund_date": self.refund_date

        }
        refund_collection.update_one({"_id": self._id}, {"$set": refund_data}, upsert=True)
        return self