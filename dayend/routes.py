from typing import List
from fastapi import APIRouter, HTTPException,status
from bson import ObjectId
from .models import Shift,ShiftPost
from .utils import get_shift_collection

router = APIRouter()

@router.post("/", response_model=str)
async def create_shift(shift: ShiftPost):
    new_shift = shift.model_dump(exclude_unset=True)  
    result = get_shift_collection().insert_one(new_shift)  # Notice the parentheses here
    return str(result.inserted_id)


def convert_to_string_or_emptys(data):
    if isinstance(data, list):
        return [str(value) if value is not None and value != "" else None for value in data]
    elif isinstance(data, (int, float)):
        return str(data)
    else:
        return str(data) if data is not None and data != "" else None


@router.get("/", response_model=List[Shift])
async def get_all_shifts():
    shifts = list(get_shift_collection().find())  # Again, parentheses
    formatted_shifts = []
    for shift in shifts:
        shift_data = {key: convert_to_string_or_emptys(value) for key, value in shift.items()}
        shift_data["shiftId"] = str(shift_data.pop("_id"))
        formatted_shifts.append(Shift(**shift_data))
    return formatted_shifts

@router.get("/{shift_id}", response_model=Shift)
async def get_shift_by_id(shift_id: str):
    shift = get_shift_collection.find_one({"_id": ObjectId(shift_id)})
    if shift:
        
        shift_data = {key: convert_to_string_or_emptys(value) for key, value in shift.items()}
        shift_data["shiftId"] = str(shift["_id"])
        return Shift(**shift_data)
    else:
        raise HTTPException(status_code=404, detail="Shift not found")


@router.patch("/{shift_id}")
async def patch_shift(shift_id: str, shift_update: ShiftPost):
    existing_shift = get_shift_collection.find_one({"_id": ObjectId(shift_id)})
    if existing_shift:
        updated_fields = shift_update.model_dump(exclude_unset=True)
      
        result = get_shift_collection.update_one(
            {"_id": ObjectId(shift_id)},
            {"$set": updated_fields}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="Failed to update shift.")
        return {"message": "Shift updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Shift not found")




@router.delete("/{shift_id}")
async def delete_shift(shift_id: str):
    result = get_shift_collection.delete_one({"_id": ObjectId(shift_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Shift not found")
    return {"message": "Shift deleted successfully"}
