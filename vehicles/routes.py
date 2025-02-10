from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import APIRouter, HTTPException,status
from .models import Vehicle, VehiclePost
from .utils import get_vehicle_collection
from bson import ObjectId
from typing import List

router = APIRouter()

mongo_client = AsyncIOMotorClient("mongodb://admin:YenE580nOOUE6cDhQERP@194.233.78.90:27017/admin?appName=mongosh+2.1.1&authSource=admin&authMechanism=SCRAM-SHA-256&replicaSet=yenerp-cluster")

def get_database(db_name="reactfluttertest"):
    return mongo_client[db_name]

def get_vehicle_collection(collection_name="vehicles"):  # Specify the default collection name if desired
    db = get_database()
    return db[collection_name]

@router.post("/", response_model=str)
async def create_vehicle(vehicle: VehiclePost):
    new_vehicle = vehicle.model_dump()
    new_vehicle.pop("id", None)
    result = get_vehicle_collection("vehicles").insert_one(new_vehicle)
    return str(result.inserted_id)


def convert_to_string_or_emptys(data):
    if isinstance(data, list):
        return [str(value) if value is not None and value != "" else None for value in data]
    elif isinstance(data, (int, float)):
        return str(data)
    else:
        return str(data) if data is not None and data != "" else None

@router.get("/", response_model=List[Vehicle])
async def get_all_vehicles():
    vehicle_collection = get_vehicle_collection("vehicles")
    vehicles = []
    async for vehicle in vehicle_collection.find():
        formatted_vehicle = {
            key: convert_to_string_or_emptys(value) for key, value in vehicle.items()
        }
        formatted_vehicle["vehicleId"] = str(vehicle["_id"])
        vehicles.append(Vehicle(**formatted_vehicle))
    return vehicles



@router.get("/{vehicle_id}", response_model=Vehicle)
async def get_vehicle_by_id(vehicle_id: str):
    vehicle = get_vehicle_collection("vehicles").find_one({"_id": ObjectId(vehicle_id)})
    if vehicle:
        formatted_vehicle = {
            key: convert_to_string_or_emptys(value) for key, value in vehicle.items()
        }
        formatted_vehicle["vehicleId"] = str(vehicle["_id"])
        return Vehicle(**formatted_vehicle)
    else:
        raise HTTPException(status_code=404, detail="Vehicle not found")


@router.put("/{vehicle_id}")
async def update_vehicle(vehicle_id: str, vehicle: VehiclePost):
    updated_vehicle = vehicle.model_dump(exclude={"id"}, exclude_unset=True)
    result = get_vehicle_collection("vehicles").update_one(
        {"_id": ObjectId(vehicle_id)}, {"$set": updated_vehicle}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return {"message": "Vehicle updated successfully"}


@router.patch("/{vehicle_id}")
async def update_vehicle(vehicle_id: str, vehicle_patch: VehiclePost):
    existing_vehicle = get_vehicle_collection("vehicles").find_one({"_id": ObjectId(vehicle_id)})
    if not existing_vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    updated_fields = {
        key: convert_to_string_or_emptys(value) for key, value in vehicle_patch.dict().items()
    }
    updated_fields = {key: value for key, value in updated_fields.items() if value is not None}

    if updated_fields:
        result = get_vehicle_collection("vehicles").update_one(
            {"_id": ObjectId(vehicle_id)},
            {"$set": updated_fields}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update vehicle")

    updated_vehicle = get_vehicle_collection("vehicles").find_one({"_id": ObjectId(vehicle_id)})
    updated_vehicle["id"] = str(updated_vehicle["_id"])  
    return Vehicle(**updated_vehicle)


@router.delete("/{vehicle_id}")
async def delete_vehicle(vehicle_id: str):
    result = get_vehicle_collection("vehicles").delete_one({"_id": ObjectId(vehicle_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return {"message": "Vehicle deleted successfully"}


