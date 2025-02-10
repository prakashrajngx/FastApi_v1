from fastapi import APIRouter, HTTPException
from typing import Any, Dict, List
from bson import ObjectId
from .models import Diningorder, DiningorderCreate, DiningorderUpdate
from .utils import get_collection

router = APIRouter()
collection = get_collection('orders')

def serialize_dict(item) -> dict:
    return {**{i: str(item[i]) for i in item if i == '_id'}, **{i: item[i] for i in item if i != '_id'}}

@router.post('/', response_model=Diningorder)
async def create_orders(order: DiningorderCreate):
    order_dict = order.dict()
    order_dict['orderId'] = str(ObjectId())
    order_dict['status'] = 'active'  # Set default status to active
    result = await collection.insert_one(order_dict)
    if result.inserted_id:
        return order_dict
    raise HTTPException(status_code=500, detail="Error creating orders order")

@router.get('/', response_model=List[Diningorder])
async def get_orders():
    orders = [serialize_dict(order) for order in await collection.find().to_list(1000)]
    return orders

@router.get('/{order_id}', response_model=Diningorder)
async def get_orders(order_id: str):
    order = await collection.find_one({'orderId': order_id})
    if order:
        return serialize_dict(order)
    raise HTTPException(status_code=404, detail="orders order not found")

@router.patch('/{order_id}', response_model=Diningorder)
async def update_orders(order_id: str, order: DiningorderUpdate):
    print(f"Updating orders order with ID: {order_id}")  # Log the ID
    result = await collection.update_one({'orderId': order_id}, {'$set': order.dict(exclude_unset=True)})
    if result.modified_count == 1:
        return serialize_dict(await collection.find_one({'orderId': order_id}))
    raise HTTPException(status_code=404, detail="orders order not found")


@router.delete('/{order_id}')
async def delete_orders(order_id: str):
    result = await collection.delete_one({'orderId': order_id})
    if result.deleted_count == 1:
        return {"message": "orders order deleted"}
    raise HTTPException(status_code=404, detail="orders order not found")

@router.patch('/patch-status/{seathiveOrderId}', response_model=List[Diningorder])
async def patch_status_by_seathiveOrderId(seathiveOrderId: str, status: str):
    """
    Patch the status of all orders with the same seathiveOrderId.
    """
    print(f"Patching status for orders with seathiveOrderId: {seathiveOrderId}")  # Log the ID
    # Find all orders with the same seathiveOrderId
    orders = await collection.find({'seathiveOrderId': seathiveOrderId}).to_list(1000)
    
    if not orders:
        raise HTTPException(status_code=404, detail="Orders with seathiveOrderId not found")

    # Update all orders with the new status
    result = await collection.update_many({'seathiveOrderId': seathiveOrderId}, {'$set': {'status': status}})
    if result.modified_count > 0:
        updated_orders = [serialize_dict(order) for order in await collection.find({'seathiveOrderId': seathiveOrderId}).to_list(1000)]
        return updated_orders
    raise HTTPException(status_code=404, detail="Orders with seathiveOrderId not found for update")

@router.patch('/patch-fields/{hiveOrderId}', response_model=Diningorder)
async def patch_fields_by_hiveOrderId(hiveOrderId: str, fields: Dict[str, Any]):
    """
    Patch specific fields of an order using hiveOrderId.
    """
    if not fields:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    # Retrieve the existing order
    order = await collection.find_one({'hiveOrderId': hiveOrderId})
    if not order:
        raise HTTPException(status_code=404, detail="Order with hiveOrderId not found")

    # Update only the provided fields
    print(f"Patching fields for order with hiveOrderId: {hiveOrderId}, Fields: {fields}")  # Log the ID and fields
    result = await collection.update_one({'hiveOrderId': hiveOrderId}, {'$set': fields})
    if result.modified_count == 1:
        return serialize_dict(await collection.find_one({'hiveOrderId': hiveOrderId}))
    raise HTTPException(status_code=404, detail="Order with hiveOrderId not found for update")

@router.patch('/patch-table-seat/{seathiveOrderId}', response_model=List[Diningorder])
async def patch_table_and_seat_by_seathiveOrderId(
    seathiveOrderId: str,
    table: int,
    seat: str
):
    """
    Update the `table` and `seat` fields for all orders with the given `seathiveOrderId`.
    """
    print(f"Patching table and seat for seathiveOrderId: {seathiveOrderId}, Table: {table}, Seat: {seat}")

    # Find matching orders
    orders = await collection.find({'seathiveOrderId': seathiveOrderId}).to_list(1000)
    if not orders:
        print(f"No orders found with seathiveOrderId: {seathiveOrderId}")
        raise HTTPException(status_code=404, detail="Orders with seathiveOrderId not found")

    # Perform update
    update_data = {'table': table, 'seat': seat}
    result = await collection.update_many({'seathiveOrderId': seathiveOrderId}, {'$set': update_data})

    if result.modified_count > 0:
        updated_orders = [serialize_dict(order) for order in await collection.find({'seathiveOrderId': seathiveOrderId}).to_list(1000)]
        return updated_orders

    raise HTTPException(status_code=404, detail="Orders with seathiveOrderId not found for update")
