from datetime import datetime
from fastapi import APIRouter, HTTPException,status
from pymongo import MongoClient
from bson import ObjectId
from typing import List

from popaymentmethod.models import PaymentMethod,PaymentMethodPost
from popaymentmethod.utils import get_popaymentmethod_collection

router = APIRouter()

@router.post("/", response_model=str,status_code=status.HTTP_201_CREATED)
async def create_payment_method(payment_method: PaymentMethodPost):
    payment_collection = get_popaymentmethod_collection()
    new_payment_method = payment_method.dict(exclude_unset=True)
    new_payment_method["created_at"] = datetime.utcnow()
    new_payment_method["updated_at"] = datetime.utcnow()
    result = payment_collection.insert_one(new_payment_method)
    return str(result.inserted_id)

@router.get("/", response_model=List[PaymentMethod])
async def get_all_payment_methods():
    payment_collection = get_popaymentmethod_collection()
    payment_methods = list(payment_collection.find())
    
    formatted_payment_methods = []
    for payment_method in payment_methods:
        payment_method_dict = {
            "paymentId": str(payment_method["_id"]),
            "paymentMethod": payment_method.get("paymentMethod"),
            "created_at": payment_method.get("created_at"),
            "updated_at": payment_method.get("updated_at")
        }
        formatted_payment_methods.append(PaymentMethod(**payment_method_dict))
    
    return formatted_payment_methods

# Get a specific payment method by ID
@router.get("/{payment_id}", response_model=PaymentMethod)
async def get_payment_method_by_id(payment_id: str):
    payment_collection = get_popaymentmethod_collection()
    payment_method = payment_collection.find_one({"_id": ObjectId(payment_id)})
    if payment_method:
        return PaymentMethod(
            **payment_method,
            paymentId=str(payment_method["_id"]),
            created_at=payment_method.get("created_at"),
            updated_at=payment_method.get("updated_at")
        )
    else:
        raise HTTPException(status_code=404, detail="Payment method not found")

# Update an existing payment method
@router.put("/{payment_id}", response_model=PaymentMethodPost)
async def update_payment_method(payment_id: str, payment_method: PaymentMethodPost):
    payment_collection = get_popaymentmethod_collection()
    updated_payment_method = payment_method.dict(exclude_unset=True)
    updated_payment_method["updated_at"] = datetime.utcnow()
    
    result = payment_collection.update_one({"_id": ObjectId(payment_id)}, {"$set": updated_payment_method})
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Payment method not found")
    
    updated_payment = payment_collection.find_one({"_id": ObjectId(payment_id)})
    return PaymentMethod(
        **updated_payment,
        paymentId=str(updated_payment["_id"]),
        created_at=updated_payment.get("created_at"),
        updated_at=updated_payment.get("updated_at")
    )

# Delete a payment method
@router.delete("/{payment_id}")
async def delete_payment_method(payment_id: str):
    payment_collection = get_popaymentmethod_collection()
    result = payment_collection.delete_one({"_id": ObjectId(payment_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Payment method not found")
    
    return {"message": "Payment method deleted successfully"}

# Get items related to a specific payment method
@router.get("/{payment_id}/items", response_model=List[str])
async def get_related_items(payment_id: str):
    payment_collection = get_popaymentmethod_collection()
    payment_method = payment_collection.find_one({"_id": ObjectId(payment_id)}, {"relatedItems": 1})
    
    if payment_method and "relatedItems" in payment_method:
        return payment_method["relatedItems"]
    else:
        raise HTTPException(status_code=404, detail="No related items found for this payment method")