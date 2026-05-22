from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import services.service_fulfillment as service_fulfillment

router = APIRouter()

class AddServiceRequest(BaseModel):
    service_id: int
    employee_id: int
    quantity: int = 1

@router.post("/booking-details/{booking_detail_id}/services")
async def add_service_to_room(booking_detail_id: int, request: AddServiceRequest):
    # Basic validation
    if not isinstance(request.service_id, int) or not isinstance(request.employee_id, int):
        raise HTTPException(400, "service_id and employee_id must be integers")

    service_id = service_fulfillment.add_service(
        booking_detail_id, request.service_id, request.employee_id, request.quantity
    )
    if not service_id:
        raise HTTPException(400, "Cannot add service: invalid service or employee or booking detail")
    return {"message": "Service added successfully"}

@router.get("/booking-details/{booking_detail_id}/services")
async def get_services_for_room(booking_detail_id: int):
    return service_fulfillment.get_services_for_room(booking_detail_id)