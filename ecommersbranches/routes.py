import re
from fastapi import APIRouter, Form, HTTPException, Query
from fastapi.responses import JSONResponse
from pymongo import DESCENDING
from pymongo.errors import DuplicateKeyError
from typing import Optional
from bson import ObjectId
from .utils import get_webbranches_collection

router = APIRouter()

photos_collection = get_webbranches_collection()

@router.post("/upload")
async def upload_photo(
    branch_name: str = Form(...),
    city_name: str = Form(...),
    contact: str = Form(...),
    map_url: Optional[str] = Form(None),  # map_url is optional
):
    """
    Upload a photo record with branch_name, city_name, contact, and optional map_url.
    Automatically generates a MongoDB ObjectId and a custom ID (e.g., 'b1', 'b2').
    """
    try:
        # Generate custom ID dynamically

        document = {
            "_id": ObjectId(),  # MongoDB ObjectId
            "branch_name": branch_name,
            "city_name": city_name,
            "contact": contact,
            "map_url": map_url
        }

        photos_collection.insert_one(document)

        return JSONResponse(
            status_code=200,
            content={
                "id": str(document["_id"]),  # MongoDB ObjectId as string
                "branch_name": branch_name,
                "city_name": city_name,
                "contact": contact,
                "map_url": map_url
            }
        )

    except DuplicateKeyError:
        raise HTTPException(
            status_code=400,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/view/{photo_id}")
async def get_photo_metadata(photo_id: str):
    """
    Retrieve metadata of a photo record by its MongoDB ObjectId.
    """
    try:
        photo_document = photos_collection.find_one({"_id": ObjectId(photo_id)})

        if photo_document:
            metadata = {
                "id": str(photo_document["_id"]),
                "custom_id": photo_document.get("custom_id", "Unknown ID"),
                "branch_name": photo_document.get("branch_name", "Unknown branch"),
                "city_name": photo_document.get("city_name", "Unknown city"),
                "contact": photo_document.get("contact", "Unknown contact"),
                "map_url": photo_document.get("map_url", "No map URL provided")
            }
            return {"metadata": metadata}
        else:
            raise HTTPException(status_code=404, detail="Photo not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/view/{photo_id}")
async def update_photo(
    photo_id: str,
    branch_name: Optional[str] = Query(None),
    city_name: Optional[str] = Query(None),
    contact: Optional[str] = Query(None),
    map_url: Optional[str] = Query(None)
):
    """
    Update a photo record's branch_name, city_name, contact, and map_url.
    """
    try:
        update_fields = {}
        if branch_name:
            update_fields["branch_name"] = branch_name
        if city_name:
            update_fields["city_name"] = city_name
        if contact:
            update_fields["contact"] = contact
        if map_url:
            update_fields["map_url"] = map_url

        if not update_fields:
            raise HTTPException(status_code=400, detail="No updates provided.")

        result = photos_collection.update_one(
            {"_id": ObjectId(photo_id)},
            {"$set": update_fields}
        )

        if result.matched_count == 1:
            return {"message": "Photo updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Photo not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/view/{photo_id}")
async def delete_photo(photo_id: str):
    """
    Delete a photo record by its MongoDB ObjectId.
    """
    try:
        photo_document = photos_collection.find_one({"_id": ObjectId(photo_id)})

        if not photo_document:
            raise HTTPException(status_code=404, detail="Photo not found")

        result = photos_collection.delete_one({"_id": ObjectId(photo_id)})

        if result.deleted_count == 1:
            return {
                "message": f"Photo from {photo_document.get('branch_name', 'Unknown branch')} deleted successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Photo not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/view")
async def get_all_photos():
    """
    Retrieve all photo records with their metadata.
    """
    try:
        photos_cursor = photos_collection.find()

        photos_list = [
            {
                "id": str(photo["_id"]),
                "custom_id": photo.get("custom_id", None),
                "branch_name": photo.get("branch_name", None),
                "city_name": photo.get("city_name", None),
                "contact": photo.get("contact", None),
                "map_url": photo.get("map_url", None)
            }
            for photo in photos_cursor
        ]

        return {"photos": photos_list}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


