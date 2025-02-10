from fastapi import APIRouter, HTTPException, Path
from typing import List
from bson import ObjectId
from .models import webaddress, webaddressPost
from .utils import get_webaddress_collection

router = APIRouter()


@router.post("/post", response_model=webaddress)
async def create_webaddress(webaddress_data: webaddressPost):
    webaddress_dict = webaddress_data.dict(exclude_unset=True)
    print("Data received:", webaddress_dict)  # Debugging: log the received data
    if not webaddress_dict:
        raise HTTPException(status_code=400, detail="No data provided to create a web address.")
    
    collection = get_webaddress_collection()
    result = collection.insert_one(webaddress_dict)
    
    inserted_webaddress = collection.find_one({"_id": result.inserted_id})
    if not inserted_webaddress:
        raise HTTPException(status_code=500, detail="Error inserting the web address.")
    
    inserted_webaddress["addressId"] = str(inserted_webaddress["_id"])
    return webaddress(**inserted_webaddress)


@router.get("/get", response_model=List[webaddress])
async def get_all_branch():
    addresses = list(get_webaddress_collection().find())
    formatted_address = []
    for address_dict in addresses:
        address_dict["addressId"] = str(address_dict["_id"])
        formatted_address.append(webaddress(**address_dict))
    return formatted_address

@router.get("/get/{address_id}", response_model=webaddress)
async def get_webaddress_by_id(address_id: str = Path(..., description="The ID of the web address to retrieve")):
    if not ObjectId.is_valid(address_id):
        raise HTTPException(status_code=400, detail="Invalid ID format.")
    address = get_webaddress_collection().find_one({"_id": ObjectId(address_id)})
    if not address:
        raise HTTPException(status_code=404, detail="Web address not found.")
    address["addressId"] = str(address["_id"])
    return webaddress(**address)

@router.patch("/update/{address_id}", response_model=webaddress)
async def update_webaddress(address_id: str, webaddress_data: webaddressPost):
    # Check if the provided ID is a valid ObjectId
    if not ObjectId.is_valid(address_id):
        raise HTTPException(status_code=400, detail="Invalid ID format.")
    
    # Get the MongoDB collection
    collection = get_webaddress_collection()
    
    # Fetch the existing document
    existing_webaddress = await collection.find_one({"_id": ObjectId(address_id)})
    if not existing_webaddress:
        raise HTTPException(status_code=404, detail="Web address not found.")
    
    # Convert the Pydantic data model to a dictionary for updating
    update_data = webaddress_data.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No data provided to update the web address.")
    
    # Remove the '_id' field from the existing data before updating
    update_data.pop("_id", None)
    
    # Perform the update operation
    result = await collection.update_one({"_id": ObjectId(address_id)}, {"$set": update_data})
    
    # Check if the update was successful
    if result.matched_count == 0:
        raise HTTPException(status_code=500, detail="Error updating the web address.")
    
    # Fetch the updated document to return
    updated_webaddress = await collection.find_one({"_id": ObjectId(address_id)})
    if not updated_webaddress:
        raise HTTPException(status_code=404, detail="Web address not found after update.")
    
    return webaddress(**updated_webaddress)  # Return the updated web address as respons




@router.delete("/delete/{address_id}", response_model=dict)
async def delete_webaddress(address_id: str):
    if not ObjectId.is_valid(address_id):
        raise HTTPException(status_code=400, detail="Invalid ID format.")
    
    collection = get_webaddress_collection()
    result = collection.delete_one({"_id": ObjectId(address_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Web address not found.")

    return {"detail": "Web address deleted successfully."}
