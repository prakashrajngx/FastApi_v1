from fastapi import APIRouter, HTTPException, Query
from bson import ObjectId
from pydantic import BaseModel, Field
from pymongo import UpdateOne
from typing import List, Dict, Optional
from .models import PaymentDone, PaymentDonePost
from .utils import get_paymentdone_collection

router = APIRouter()

# Utility function to get the next counter value for PaymentDone
def get_next_payment_done_counter_value():
    counter_collection = get_paymentdone_collection().database["counters"]
    counter = counter_collection.find_one_and_update(
        {"_id": "paymentDoneId"},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )
    return counter["sequence_value"]

# Reset the counter for PaymentDone (optional if needed)
def reset_payment_done_counter():
    counter_collection = get_paymentdone_collection().database["counters"]
    counter_collection.update_one(
        {"_id": "paymentDoneId"},
        {"$set": {"sequence_value": 0}},
        upsert=True
    )

# Generate the random ID for PaymentDone using the counter
def generate_payment_done_random_id():
    counter_value = get_next_payment_done_counter_value()
    return f"PD{counter_value:03d}"  # This will generate IDs like PD001, PD002, etc.

@router.post("/", response_model=str)
async def create_payment_done(payment_done: PaymentDonePost):
    collection = get_paymentdone_collection()

    # If this is the first PaymentDone record, reset the counter
    if collection.count_documents({}) == 0:
        reset_payment_done_counter()

    # Generate random ID for the new PaymentDone
    random_id = generate_payment_done_random_id()
    
    # Add randomId to the payment_done data
    payment_done_data = payment_done.dict()
    payment_done_data['randomId'] = random_id

    # Insert into the collection
    result = collection.insert_one(payment_done_data)
    
    return str(result.inserted_id)

@router.get("/", response_model=List[PaymentDone])
async def get_paymentdone():
    # Find the payment record by ObjectId
    payment = list(get_paymentdone_collection().find())
    formatted_payment=[]    
    for payments in payment:
        # Convert ObjectId to string for the response
        payments["paymentDoneId"] = str(payments["_id"])
        formatted_payment.append(PaymentDone(**payments))  # Assuming PaymentDone is your Pydantic model
    return formatted_payment

@router.get("/{paymentdone_id}", response_model=PaymentDone)
async def get_paymentdone_by_id(paymentdone_id: str):
    # Find the payment record by ObjectId
    payment = get_paymentdone_collection().find_one({"_id": ObjectId(paymentdone_id)})
    
    if payment:
        # Convert ObjectId to string for the response
        payment["paymentDoneId"] = str(payment["_id"])
        return PaymentDone(**payment)  # Assuming PaymentDone is your Pydantic model
    else:
        raise HTTPException(status_code=404, detail="Payment record not found")


# PUT route to update an existing PaymentDone record by ID
@router.put("/{paymentdone_id}", response_model=Dict[str, str])
async def update_payment_done(paymentdone_id: str, payment_done: PaymentDonePost):
    collection = get_paymentdone_collection()

    # Convert request body to dict and update record
    updated_data = payment_done.dict(exclude_unset=True)
    
    result = collection.replace_one({"_id": ObjectId(paymentdone_id)}, updated_data)
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Payment Done record not found")
    
    return {"message": "Payment Done updated successfully"}

# PATCH route to partially update a PaymentDone record by ID
@router.patch("/{paymentdone_id}", response_model=Dict[str, str])
async def patch_payment_done(paymentdone_id: str, payment_done: PaymentDonePost):
    collection = get_paymentdone_collection()

    # Fetch the existing record
    existing_payment_done = collection.find_one({"_id": ObjectId(paymentdone_id)})
    
    if existing_payment_done is None:
        raise HTTPException(status_code=404, detail="Payment Done record not found")

    # Only update the fields that are provided
    updated_fields = {k: v for k, v in payment_done.dict(exclude_unset=True).items() if v is not None}
    
    result = collection.update_one({"_id": ObjectId(paymentdone_id)}, {"$set": updated_fields})
    
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update Payment Done record")
    
    return {"message": "Payment Done updated successfully"}

# DELETE route to remove a PaymentDone record by ID
@router.delete("/{paymentdone_id}", response_model=Dict[str, str])
async def delete_payment_done(paymentdone_id: str):
    collection = get_paymentdone_collection()

    result = collection.delete_one({"_id": ObjectId(paymentdone_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Payment Done record not found")
    
    return {"message": "Payment Done record deleted successfully"}
