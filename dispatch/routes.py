from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from bson import ObjectId
from datetime import datetime, timedelta
from .models import Dispatch, DispatchPost, get_iso_datetime
from .utils import get_dispatch_collection

router = APIRouter()

@router.post("/", response_model=dict)
async def create_dispatch(dispatch: DispatchPost):
    
    new_dispatch_data = dispatch.dict()

    # Insert into MongoDB
    result = get_dispatch_collection().insert_one(new_dispatch_data)

    # Return the inserted ID and the posted date
    return {
        "inserted_id": str(result.inserted_id),
        "date": new_dispatch_data.get("date", get_iso_datetime())
    }



@router.get("/", response_model=List[Dispatch]) 
async def get_all_dispatch_entries(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
):
    """
    Fetch all dispatch entries, optionally filtering by a start and end date,
    excluding entries with a 'Cancel' status.

    :param start_date: A string in DD-MM-YYYY format indicating the start of the date range.
    :param end_date: A string in DD-MM-YYYY format indicating the end of the date range.
    :return: A list of Dispatch objects.
    """
    query = {"status": {"$ne": "Cancel"}}  # Exclude cancelled dispatches

    if start_date or end_date:
        try:
            date_filter = {}
            if start_date:
                start_date_obj = datetime.strptime(start_date, "%d-%m-%Y")
                start_date_iso = start_date_obj.replace(
                    hour=0, minute=0, second=0, microsecond=0
                ).isoformat()
                date_filter["$gte"] = start_date_iso

            if end_date:
                end_date_obj = datetime.strptime(end_date, "%d-%m-%Y")
                end_date_obj = end_date_obj.replace(
                    hour=23, minute=59, second=59, microsecond=999999
                )
                end_date_iso = end_date_obj.isoformat()
                date_filter["$lte"] = end_date_iso

            if date_filter:
                query["date"] = date_filter

        except ValueError:
            raise HTTPException(
                status_code=400, detail="Invalid date format. Use DD-MM-YYYY."
            )

    dispatch_entries = list(get_dispatch_collection().find(query))

    # Format and serialize the entries
    formatted_dispatch_entries = []
    for entry in dispatch_entries:
        entry["dispatchId"] = str(entry["_id"])  # Convert ObjectId to string
        formatted_dispatch_entries.append(Dispatch(**entry))

    return formatted_dispatch_entries


@router.get("/{dispatch_id}", response_model=Dispatch)
async def get_dispatch_by_id(dispatch_id: str):
    """
    Fetch a dispatch entry by its ID.

    :param dispatch_id: The ID of the dispatch entry.
    :return: The Dispatch object.
    
    """
    dispatch = get_dispatch_collection().find_one({"_id": ObjectId(dispatch_id)})
    if dispatch:
        dispatch["dispatchId"] = str(dispatch["_id"])
        return Dispatch(**dispatch)
    else:
        raise HTTPException(status_code=404, detail="Dispatch not found")

@router.put("/{dispatch_id}")
async def update_dispatch(dispatch_id: str, dispatch: DispatchPost):
    """
    Update an existing dispatch entry.

    :param dispatch_id: The ID of the dispatch entry.
    :param dispatch: DispatchPost object with updated data.
    :return: Success message.
    """
    updated_dispatch = dispatch.dict(exclude_unset=True)  # Exclude unset fields
    result = get_dispatch_collection().update_one({"_id": ObjectId(dispatch_id)}, {"$set": updated_dispatch})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Dispatch not found")
    return {"message": "Dispatch updated successfully"}

@router.patch("/{dispatch_id}")
async def patch_dispatch(dispatch_id: str, dispatch_patch: DispatchPost):
    """
    Partially update an existing dispatch entry.

    :param dispatch_id: The ID of the dispatch entry.
    :param dispatch_patch: DispatchPost object with fields to update.
    :return: The updated Dispatch object.
    """
    existing_dispatch = get_dispatch_collection().find_one({"_id": ObjectId(dispatch_id)})
    if not existing_dispatch:
        raise HTTPException(status_code=404, detail="Dispatch not found")

    updated_fields = {key: value for key, value in dispatch_patch.dict(exclude_unset=True).items() if value is not None}
    if updated_fields:
        result = get_dispatch_collection().update_one({"_id": ObjectId(dispatch_id)}, {"$set": updated_fields})
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update Dispatch")

    updated_dispatch = get_dispatch_collection().find_one({"_id": ObjectId(dispatch_id)})
    updated_dispatch["_id"] = str(updated_dispatch["_id"])
    return updated_dispatch

@router.delete("/{dispatch_id}")
async def delete_dispatch(dispatch_id: str):
    """
    Delete a dispatch entry by its ID.

    :param dispatch_id: The ID of the dispatch entry.
    :return: Success message.
    """
    result = get_dispatch_collection().delete_one({"_id": ObjectId(dispatch_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Dispatch not found")
    return {"message": "Dispatch deleted successfully"}