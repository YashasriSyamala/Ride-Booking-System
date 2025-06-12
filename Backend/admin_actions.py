from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt
from app.models.Booking import Booking
from app.utils.response import Response
from app.models.Rides import Rides
from app.models.Rider import Rider
from app.models.Driver import Driver
from app.utils.constants import DriverStatus

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

@admin_bp.route("/myearnings",methods=['GET'])
@jwt_required()
def get_admin_earnings():
    result = Booking.calculate_admin_earnings()
    return Response.generate(
        status=200,
        data= result,
        message='Admin Earnings Fetched SuccessFully'
    )

@admin_bp.route("/get_all_rides", methods={"GET"})
@jwt_required()
def get_all_rides():
    try:
        role = get_jwt()["role"]

        if role != "admin":
            return Response.generate(
                status=401, message="You are not allowed to perform this action"
        )
        rides = Rides.get_all_rides()
        result = []
        for ride in rides:
            ride_dict = ride.to_dict()
            list_of_rider_names = []
            for rider_id in ride.list_of_riders:
                list_of_rider_names.append(Rider.get_by_id(user_id=rider_id).username)
            ride_dict["list_of_riders"] = list_of_rider_names
            ride_dict["driver_name"] = Driver.get_by_id(ride.driver_id).username
            result.append(ride_dict)
            ride_dict["admin_commission"] = Booking.calculate_admin_earnings(ride_id=ride._id)
        admin_earnings = Booking.calculate_admin_earnings()


        return Response.generate(
            status=200, data={"admin_earnings": admin_earnings, "list_of_rides":result}
        )

    except Exception as error:
        return Response.generate(status=500, message=str(error))

@admin_bp.route("/get_requests",methods={"GET"})
@jwt_required()
def get_requests():
    try:
        role = get_jwt()["role"]
        if role !="admin":
            return Response.generate(status=401, message="You are not allowed to perform this action")
        list_of_pending_drivers = Driver.get_pending_drivers()
        return Response.generate(status=200, data=list_of_pending_drivers)

        pass
    except Exception as error:
        return Response.generate(status=500, message=str(error))

@admin_bp.route("/approve_driver", methods=["POST"])
@jwt_required()
def approve_driver():
    try:
        data = request.get_json()
        driver_id = data["driver_id"]
        action = data["action"]
        driver = Driver.get_by_id(driver_id)
        if action == "approve":
            driver.status = DriverStatus.APPROVED.value
            driver.save()
            return Response.generate(status=200,  message="Driver approved.")
        if action == "reject":
            driver.status = DriverStatus.REJECTED.value
            driver.save()
            return Response.generate(status=200,  message="Driver approved.")
        else:
            return Response.generate(status=400, message="Invalid Action")

    except Exception as error:
        return Response.generate(status=500, message=str(error))