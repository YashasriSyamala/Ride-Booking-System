from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from app.utils.response import Response
from app.utils.get_roles import get_user_collection_by_role
from app.models.Rides import Rides
from app.utils.constants import RideStatus, PaymentStatus
from datetime import datetime
from app.models.Driver import Driver
from app.models.Booking import Booking
from app.models.Refund import Refund
from app.models.Rider import Rider
from app.models.Payment import Payment
from app.models.Ride_riders import Rides_rider
from app.utils.send_email import SendMail
from app.utils.require_approval_driver import require_approval

driver_bp = Blueprint("driver", __name__, url_prefix="/api/driver")


@driver_bp.route("/add_license_number", methods=["POST"])
@jwt_required()
def add_license_number():
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        role = get_jwt()["role"]

        if role != "driver":
            return Response.generate(
                status=401, message="You are not allowed to perform this action"
            )

        user = get_user_collection_by_role(role)
        user_obj = user.get_by_id(user_id)
        user_obj.license_number = data["license_number"]
        user_obj.save()
        return Response.generate(
            status=200, message="License number added successfully"
        )

    except Exception as e:
        return Response.generate(status=500, message=str(e))


@driver_bp.route("/get_license_number", methods=["POST"])
@jwt_required()
def get_license_number():
    try:
        user_id = get_jwt_identity()
        role = get_jwt()["role"]
        if role != "driver":
            return Response.generate(
                status=401, message="You are not allowed to perform this action"
            )
        user = get_user_collection_by_role(role)
        user_obj = user.get_by_id(user_id)
        return Response.generate(
            status=200, data={"license_number": user_obj.license_number}
        )
    except Exception as e:
        return Response.generate(status=500, message=str(e))


@driver_bp.route("/add_vehicle", methods=["POST"])
@jwt_required()
@require_approval
def add_vehicle():
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        role = get_jwt()["role"]
        vehicle_info = data["vehicle_info"]

        if role != "driver":
            return Response.generate(
                status=401, message="You are not allowed to perform this action"
            )

        result = Driver.add_vehicle_info(user_id, vehicle_info)
        return Response.generate(
            data=result, message="vehicle added successfully", status=200
        )

    except KeyError as e:
        return Response.generate(
            status=400, message=f"KeyError: Missing required attribute: {e}"
        )

    except Exception as e:
        return Response.generate(status=500, message=str(e))


@driver_bp.route("/create_ride", methods=["POST"])
@jwt_required()
@require_approval
def create_ride():
    try:
        data = request.get_json()
        pickup_location = data["pickup_location"]
        drop_location = data["drop_location"]
        vehicle_id = data["vehicle_id"]
        available_seats = data["capacity"]
        price_per_seat = data["price_per_seat"]
        start_time_str = data["start_time"]
        start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%S%z")

        user_id = get_jwt_identity()
        role = get_jwt()["role"]

        if role != "driver":
            return Response.generate(
                status=403, message="You are not allowed to perform this action"
            )

        rides_obj = Rides(
            pickup_location=pickup_location,
            drop_location=drop_location,
            vehicle_id=vehicle_id,
            available_seats=available_seats,
            price_per_seat=price_per_seat,
            start_time=start_time,
            driver_id=user_id,
            status=RideStatus.SCHEDULED.value,
        )
        rides_obj.create_ride()
        return Response.generate(status=200, message="Ride created successfully")
    except Exception as e:
        return Response.generate(message=str(e))


@driver_bp.route("/get_all_rides", methods=["Get"])
@jwt_required()
def get_all_rides_driver():
    try:
        user_id = get_jwt_identity()
        role = get_jwt()["role"]

        if role != "driver":
            return Response.generate(
                status=403, message="You are not allowed to perform this action"
            )

        results = Rides.get_all_rides_driver({"driver_id": user_id})

    except KeyError as e:
        return Response.generate(
            status=400, message=f"KeyError: Missing required attribute: {e}"
        )
    except Exception as e:
        return Response.generate(message=str(e))
    else:
        return Response.generate(status=200, data=results)


@driver_bp.route("/cancel_ride", methods=["POST"])
@jwt_required()
@require_approval
def cancel_ride():
    try:
        user_id = get_jwt_identity()
        role = get_jwt()["role"]
        data = request.get_json()
        ride_id = data["ride_id"]

        if role != "driver":
            return Response.generate(
                status=403, message="You are not allowed to perform this action"
            )
        result = Rides.cancel_ride(ride_id=ride_id, driver_id=user_id)
        if result != 1:
            return Response.generate(status=500, message="can not find ride")
        list_of_bookings = Booking.get_all_bookings_by_ride_id(ride_id=ride_id)

        for booking in list_of_bookings:
            refund = Refund(
                booking_id=booking._id,
                rider_id=booking.rider_id,
                amount_refunded=(booking.admin_commission + booking.driver_earning),
                payment_id=booking.payment_id,
                refund_status="DONE",
            )
            refund.save()
            payment = Payment.get_by_id(booking.payment_id)
            payment.payment_status = PaymentStatus.REFUNDED.value
            payment.save()
            booking.admin_commission = 0
            booking.driver_earning = 0
            booking.save()
        ride = Rides.get_ride_by_id(ride_id)
        recipients= []
        for rider in ride.list_of_riders:
            recipients.append(Rider.get_by_id(rider).email)
        obj = Rides_rider.get_by_ride_id(ride_id)
        if obj is not None:
            obj.status = RideStatus.CANCELLED.value
            obj.save()
        if len(recipients) !=0:
            SendMail.send_email(recipients=recipients, ride=ride )
    except KeyError as e:
        return Response.generate(
            status=400, message=f"KeyError: Missing required attribute: {e}"
        )

    except Exception as e:
        return Response.generate(message=str(e))

    else:
        return Response.generate(status=200, message="cancelled ride successfully!!")


@driver_bp.route("/driver_earning", methods=["POST"])
@jwt_required()
def get_my_earning():
    driver_id = get_jwt_identity()
    result = Booking.calculate_driver_earnings(driver_id=driver_id)
    return Response.generate(
        status=200, data=result, message="driver earnings fetched successfully"
    )


@driver_bp.route("/get_vehicles_list", methods=["GET"])
@jwt_required()
def get_vehicles_list():
    try:
        user_id = get_jwt_identity()
        role = get_jwt()["role"]

        if role != "driver":
            return Response.generate(
                status=403, message="You are not allowed to perform this action"
            )
        result = Driver.get_all_vehicles(driver_id=user_id)
        return Response.generate(
            status=200, data=result, message="vehicles list fetched successfully"
        )
    except Exception as e:
        return Response.generate(message=str(e))


@driver_bp.route("get_bookings", methods={"POST"})
@jwt_required()
def get_bookings():
    try:
        data = request.get_json()
        ride_id = data["ride_id"]


        bookings = Booking.get_all_bookings_by_ride_id(ride_id=ride_id)
        list_of_bookings = []
        for booking in bookings:
            rider_name = Rider.get_by_id(user_id=str(booking.rider_id)).username
            rider_contact =Rider.get_by_id(user_id=booking.rider_id).phone_number
            payment_details = Payment.get_by_id(payment_id=booking.payment_id).to_dict()
            list_of_bookings.append({
                "rider_name": rider_name,
                "payment_details": payment_details,
                "rider_pickup_location": booking.rider_pickup_location,
                "created_at": booking.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                "rider_contact": rider_contact
            })

        earnings = Booking.calculate_driver_earnings_for_a_ride(ride_id=ride_id)
        result = {
            "bookings": list_of_bookings,
            "earnings": earnings
        }

        return Response.generate(
            status=200, data=result
        )
    except Exception as e:
        return Response.generate(message=str(e))
    
@driver_bp.route("/delete_vehicle", methods=["POST"])
@jwt_required()
@require_approval
def delete_vehicle():
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        role = get_jwt()["role"]
        license_plate = data["license_plate"]

        if role != "driver":
            return Response.generate(
                status=401, message="You are not allowed to perform this action"
            )
        result = Driver.delete_vehicle(user_id, license_plate)
        return Response.generate(
            status=200, message="vehicle deleted successfully", data=result
        )
    except Exception as e:
        return Response.generate(status=500, message=str(e))
