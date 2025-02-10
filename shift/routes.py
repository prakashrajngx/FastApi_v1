import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query,status
from bson import ObjectId
from .models import Shift,ShiftPost
from .utils import get_shift_collection
from datetime import datetime

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





@router.get("/openingbalance/", response_model=dict)
async def get_manual_opening_balance_by_branch_date(branch_name: str, date: str) -> Optional[dict]:
    # Parse the date string into a datetime object
    try:
        date_parsed = datetime.strptime(date, "%d-%m-%Y")
        date_str = date_parsed.strftime("%d-%m-%Y")  # Ensure the date format matches the stored format in the database
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Please use DD-MM-YYYY.")

    # Query to find the shift by branch name and date
    shift = get_shift_collection().find_one({
        "branchName": branch_name,
        "shiftOpeningDate": date_str,
        "dayEndStatus": "open",
        "status": "open"
    })

    if not shift:
        raise HTTPException(status_code=404, detail="No open shift found for given branch name and date.")

    manual_balance = shift.get("manualOpeningBalance", "0")  
    return {"manualOpeningBalance": str(manual_balance)}