
# from typing import List, Optional
# from fastapi import APIRouter, Body, HTTPException, Query, logger
# from bson import ObjectId
# from pydantic import BaseModel
# from .models import Invoice, SalesOrder, SalesOrderPost
# from .utils import get_invoice_collection, get_salesOrder_collection
# import logging
# from datetime import datetime
# from bson.errors import InvalidId
# import requests


# router = APIRouter()

# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
# logger = logging.getLogger(__name__)

# def convert_to_date(date_str: str) -> datetime:
#     """
#     Converts a date string in "dd-MM-yyyy" format to a datetime object.
#     Raises an exception if the format is invalid.
#     """
#     try:
#         return datetime.strptime(date_str, "%d-%m-%Y")
#     except ValueError:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Invalid date format: {date_str}. Please use dd-MM-yyyy."
#         )
    
# def fetch_sales_orders(query: dict) -> List[dict]:
#     """
#     Fetches sales orders from MongoDB based on the query.

#     Args:
#         query (dict): MongoDB query dictionary.

#     Returns:
#         List[dict]: List of sales orders retrieved from the database.
#     """
#     try:
#         # Get the collection
#         collection = get_salesOrder_collection()

#         # Execute the query
#         logger.debug(f"Executing MongoDB query: {query}")
#         results = list(collection.find(query))

#         logger.info(f"Retrieved {len(results)} records from MongoDB.")
#         return results
#     except Exception as e:
#         logger.error(f"Error querying MongoDB: {e}", exc_info=True)
#         raise    

# def serialize_document(order: dict):
#     if isinstance(order["_id"], ObjectId):
#         # Store the _id in salesOrderId for easier access
#         order["salesOrderId"] = str(order["_id"])  # Convert ObjectId to string and store it in salesOrderId
#         del order["_id"]  # Optionally remove the _id field, since it's now in salesOrderId
    
#     # Convert deliveryDate to dd-mm-yyyy
#     if order.get("deliveryDate"):
#         order["deliveryDate"] = format_date_to_ddmmyyyy(order["deliveryDate"])
    
#     return order


# def format_date_to_ddmmyyyy(date: datetime) -> str:
#     return date.strftime("%d-%m-%Y")

# @router.post("/", response_model=str)
# async def create_salesOrder(salesOrder: SalesOrderPost):
#     # Convert the incoming deliveryDate to datetime object
#     delivery_data = convert_to_date(salesOrder.deliveryDate)
#     # order_date = datetime.now() if not salesOrder.orderDate else convert_to_date(salesOrder.orderDate)

#     # Prepare the new sales order data for insertion
#     new_salesOrder_data = {**salesOrder.dict(), "deliveryDate": delivery_data}

#     # Insert into MongoDB
#     result = get_salesOrder_collection().insert_one(new_salesOrder_data)
#     return str(result.inserted_id)

# @router.get("/")
# async def get_sales_orders(
#     deliveryStartDate: Optional[str] = Query(None),
#     deliveryEndDate: Optional[str] = Query(None),
#     deliveryDate: Optional[str] = Query(None),
#     customerNumber: Optional[str] = None,
#     customerName: Optional[str] = None,
#     orderDate: Optional[str] = None,
#     paymentType: Optional[str] = None,
#     minAdvanceAmount: Optional[float] = None,
#     salesOrderLast5Digits: Optional[str] = None,
#     filterCreditCustomer: Optional[bool] = Query(False, alias="filter-credit-customer"),
#     filterCreditCustomerPreinvoice: Optional[bool] = Query(False, alias="filter-credit-customer-preinvoice")

# ):
#     """
#     Fetch sales orders based on query parameters, including an optional filter for credit customers.
    
#     """
#     try:
#         logger.info("Received request to fetch sales orders.")
#         # Prepare query based on input parameters
#         query = {}
#         # Date filters
#         if deliveryStartDate and deliveryEndDate:
#             start_date = datetime.strptime(deliveryStartDate, "%d-%m-%Y")
#             end_date = datetime.strptime(deliveryEndDate, "%d-%m-%Y").replace(hour=23, minute=59, second=59)
#             query["deliveryDate"] = {"$gte": start_date, "$lte": end_date}

#         elif deliveryDate:
#             specific_date = datetime.strptime(deliveryDate, "%d-%m-%Y")
#             query["deliveryDate"] = specific_date

#         # Customer filters
#         if customerName:
#             query["customerName"] = {"$regex": customerName, "$options": "i"}

#         if customerNumber:
#             query["customerNumber"] = {"$regex": customerNumber, "$options": "i"}

#         # Sales order ID filter
#         if salesOrderLast5Digits:
#             query["_id"] = {"$regex": f".*{salesOrderLast5Digits}$", "$options": "i"}

#         # Filter for credit customers if requested
#         if filterCreditCustomer:
#             query["creditCustomerOrder"] = "yes"
#             logger.info("Applied filter for credit customer orders only.")
#         if filterCreditCustomerPreinvoice:
#             query["creditCustomerOrder"] = "credit sales order pre invoiced"
#             logger.info("Applied filter for credit customer pre invoiced only.")

#         # Fetch data from MongoDB
#         raw_orders = fetch_sales_orders(query)
#         serialized_orders = [serialize_document(order) for order in raw_orders]

#         logger.info(f"Formatted {len(serialized_orders)} sales orders for the response.")
#         return serialized_orders

#     except Exception as e:
#         logger.error(f"An error occurred: {e}", exc_info=True)
#         raise HTTPException(status_code=500, detail="Internal Server Error")
    
    
    
# @router.get("/{salesOrder_id}", response_model=SalesOrder)
# async def get_salesOrder_by_id(salesOrder_id: str):
#     salesOrder = get_salesOrder_collection().find_one({"_id": ObjectId(salesOrder_id)})
#     if salesOrder:
#         salesOrder["salesOrderId"] = str(salesOrder["_id"])
#         return SalesOrder(**salesOrder)
#     else:
#         raise HTTPException(status_code=404, detail="SalesOrder not found")



# @router.patch("/{salesOrder_id}")
# async def patch_salesOrder(salesOrder_id: str, salesOrder_patch: SalesOrderPost):
#     existing_salesOrder = get_salesOrder_collection().find_one({"_id": ObjectId(salesOrder_id)})
#     if not existing_salesOrder:
#         raise HTTPException(status_code=404, detail="salesOrder not found")

#     updated_fields = {key: value for key, value in salesOrder_patch.dict(exclude_unset=True).items() if value is not None}
#     if updated_fields:
#         result = get_salesOrder_collection().update_one({"_id": ObjectId(salesOrder_id)}, {"$set": updated_fields})
#         if result.modified_count == 0:
#             raise HTTPException(status_code=500, detail="Failed to update salesOrder")

#     updated_salesOrder = get_salesOrder_collection().find_one({"_id": ObjectId(salesOrder_id)})
#     updated_salesOrder["_id"] = str(updated_salesOrder["_id"])
#     return updated_salesOrder

# @router.delete("/{salesOrder_id}")
# async def delete_salesOrder(salesOrder_id: str):
#     result = get_salesOrder_collection().delete_one({"_id": ObjectId(salesOrder_id)})
#     if result.deleted_count == 0:
#         raise HTTPException(status_code=404, detail="salesOrder not found")
#     return {"message": "salesOrder deleted successfully"}




# @router.get("/soadvancedtotalcash", response_model=List[SalesOrder])
# async def get_sales_orders(
   
#     orderDate: Optional[str] = None,
#     paymentType: Optional[str] = None,
#     minAdvanceAmount: Optional[float] = None,
# ):
#     """
#     Retrieve sales orders based on customerNumber, customerName, deliveryDate, orderDate,
#     paymentType, and advanceAmount.
    
#     """
#     # Build the query dynamically based on the provided filters
#     query = {}
    
#     if orderDate:
#         query["orderDate"] = orderDate
#     if paymentType:
#         query["paymentType"] = paymentType
#     if minAdvanceAmount is not None:
#         query["advanceAmount"] = {"$gt": minAdvanceAmount}  # Greater than specified advanceAmount

#     # Log the query for debugging
#     logging.info(f"Executing query: {query}")

#     # Fetch sales orders matching the query
#     salesOrders = list(get_salesOrder_collection().find(query))

#     if not salesOrders:
#         raise HTTPException(status_code=404, detail="No sales orders found for the given criteria.")

#     # Format the response
#     formatted_salesOrders = [
#         SalesOrder(**{**order, "salesOrderId": str(order["_id"])}) for order in salesOrders
#     ]

#     return formatted_salesOrders

# @router.patch("/create_invoice/{salesOrder_id}")
# async def create_invoice_from_sales_order(salesOrder_id: str):
#     # Fetch the sales order
#     sales_order = await get_salesOrder_collection().find_one({"_id": ObjectId(salesOrder_id)})

#     if not sales_order:
#         raise HTTPException(status_code=404, detail="Sales Order not found")

#     # Map sales order data to invoice model
#     invoice_data = Invoice(
#         itemName=sales_order.get("itemName"),
#         varianceName=sales_order.get("varianceName"),
#         price=sales_order.get("price"),
#         weight=sales_order.get("weight"),
#         qty=sales_order.get("qty"),
#         amount=sales_order.get("amount"),
#         tax=sales_order.get("tax"),
#         uom=sales_order.get("uom"),
#         totalAmount=sales_order.get("totalAmount"),
#         totalAmount2=sales_order.get("totalAmount2"),
#         totalAmount3=sales_order.get("totalAmount3"),
#         status=sales_order.get("status"),
#         salesType=sales_order.get("salesType"),
#         customerPhoneNumber=sales_order.get("customerPhoneNumber", "No Number"),
#         employeeName=sales_order.get("employeeName"),
#         branchId=sales_order.get("branchId"),
#         branchName=sales_order.get("branchName"),
#         paymentType=sales_order.get("paymentType"),
#         cash=sales_order.get("cash"),
#         card=sales_order.get("card"),
#         upi=sales_order.get("upi"),
#         others=sales_order.get("others"),
#         invoiceDate=datetime.now().strftime("%d-%m-%Y"),
#         invoiceTime=datetime.now().strftime("%H:%M:%S"),
#         shiftNumber=sales_order.get("shiftNumber"),
#         shiftId=sales_order.get("shiftId"),
#         invoiceNo="INV" + str(ObjectId()),  # Generate Invoice Number
#         deviceNumber=sales_order.get("deviceNumber"),
#         customCharge=sales_order.get("customCharge"),
#         discountAmount=sales_order.get("discountAmount"),
#         discountPercentage=sales_order.get("discountPercentage"),
#         user=sales_order.get("user"),
#         # deviceCode=sales_order.get("deviceCode")
#     )

#     # Insert the invoice data into the invoice collection
#     invoice_collection = get_invoice_collection()
#     invoice_result = await invoice_collection.insert_one(invoice_data.dict())

#     # Update the status of the sales order
#     update_result = await get_salesOrder_collection().update_one(
#         {"_id": ObjectId(salesOrder_id)},
#         {"$set": {"status": "Invoiced"}}
#     )

#     if update_result.modified_count == 0:
#         raise HTTPException(status_code=500, detail="Failed to update the sales order status")

#     return {"message": "Sales Order status updated and Invoice created successfully", "invoiceId": str(invoice_result.inserted_id)}




#     # credit sales order patch method for multiple IDs
# @router.patch("/crsopreinvoice/")
# async def patch_multiple_credit_sales_orders_pre_invoiced(salesOrder_ids: List[str]):
#         """
#         Updates multiple sales orders to set `creditCustomerOrder` to
#         "credit sales order pre invoiced".

#         Args:
#             salesOrder_ids (List[str]): The list of sales order IDs to update.

#         Returns:
#             dict: The updated sales orders or an error message if not found.
#         """
#         try:
#             updated_sales_orders = []
#             for salesOrder_id in salesOrder_ids:
#                 # Validate and convert the salesOrder_id to ObjectId
#                 try:
#                     object_id = ObjectId(salesOrder_id)
#                 except InvalidId as e:
#                     raise HTTPException(
#                         status_code=400,
#                         detail=f"Invalid salesOrder_id: {e}"
#                     )

#                 # Find the sales order by ID
#                 existing_sales_order = get_salesOrder_collection().find_one({"_id": object_id})
#                 if not existing_sales_order:
#                     raise HTTPException(
#                         status_code=404,
#                         detail=f"Sales order not found for ID: {salesOrder_id}"
#                     )

#                 # Update the sales order
#                 update_data = {
#                     "$set": {
#                         "creditCustomerOrder": "credit sales order pre invoiced"
#                     }
#                 }
#                 result = get_salesOrder_collection().update_one({"_id": object_id}, update_data)

#                 if result.modified_count == 0:
#                     raise HTTPException(
#                         status_code=500,
#                         detail=f"Failed to update the sales order for ID: {salesOrder_id}"
#                     )

#                 # Fetch the updated sales order
#                 updated_sales_order = get_salesOrder_collection().find_one({"_id": object_id})
#                 updated_sales_order["_id"] = str(updated_sales_order["_id"])  # Convert ObjectId to string
#                 updated_sales_orders.append(updated_sales_order)

#             return {
#                 "message": "Sales orders updated successfully",
#                 "salesOrders": updated_sales_orders
#             }

#         except Exception as e:
#             logger.error(f"Error during update: {e}", exc_info=True)
#             raise HTTPException(status_code=500, detail="Internal Server Error")

# @router.patch("/crsoinvoice/")
# async def patch_multiple_credit_sales_orders_pre_invoiced(salesOrder_ids: List[str]):
#         """
#         Updates multiple sales orders to set `creditCustomerOrder` to
#         "credit sales order pre invoiced".

#         Args:
#             salesOrder_ids (List[str]): The list of sales order IDs to update.

#         Returns:
#             dict: The updated sales orders or an error message if not found.
            
#         """
#         try:
#             updated_sales_orders = []
#             for salesOrder_id in salesOrder_ids:
#                 # Validate and convert the salesOrder_id to ObjectId
#                 try:
#                     object_id = ObjectId(salesOrder_id)
#                 except InvalidId as e:
#                     raise HTTPException(
#                         status_code=400,
#                         detail=f"Invalid salesOrder_id: {e}"
#                     )

#                 # Find the sales order by ID
#                 existing_sales_order = get_salesOrder_collection().find_one({"_id": object_id})
#                 if not existing_sales_order:
#                     raise HTTPException(
#                         status_code=404,
#                         detail=f"Sales order not found for ID: {salesOrder_id}"
#                     )

#                 # Update the sales order
#                 update_data = {
#                     "$set": {
#                         "creditCustomerOrder": "credit sales order invoiced"
#                     }
#                 }
#                 result = get_salesOrder_collection().update_one({"_id": object_id}, update_data)

#                 if result.modified_count == 0:
#                     raise HTTPException(
#                         status_code=500,
#                         detail=f"Failed to update the sales order for ID: {salesOrder_id}"
#                     )

#                 # Fetch the updated sales order
#                 updated_sales_order = get_salesOrder_collection().find_one({"_id": object_id})
#                 updated_sales_order["_id"] = str(updated_sales_order["_id"])  # Convert ObjectId to string
#                 updated_sales_orders.append(updated_sales_order)

#             return {
#                 "message": "Sales orders updated successfully",
#                 "salesOrders": updated_sales_orders
#             }

#         except Exception as e:
#             logger.error(f"Error during update: {e}", exc_info=True)
#             raise HTTPException(status_code=500, detail="Internal Server Error")


# # def update_multiple_sales_orders(base_url, salesOrder_ids):
# #     results = []
# #     for salesOrder_id in salesOrder_ids:
# #         try:
# #             response = requests.patch(f"{base_url}/crsopreinvoice/{salesOrder_id}")
# #             response.raise_for_status()
# #             results.append({
# #                 "salesOrder_id": salesOrder_id,
# #                 "status": "success",
# #                 "details": response.json()
# #             })
# #         except requests.exceptions.RequestException as e:
# #             results.append({
# #                 "salesOrder_id": salesOrder_id,
# #                 "status": "failed",
# #                 "details": str(e)
# #             })
# #     return results


from typing import List, Optional
from fastapi import APIRouter, Body, HTTPException, Query, logger
from bson import ObjectId
from pydantic import BaseModel
from .models import Invoice, SalesOrder, SalesOrderPost
from .utils import  get_invoice_collection, get_salesOrder_collection
import logging
from datetime import datetime
from bson.errors import InvalidId

router = APIRouter()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def convert_to_date(date_str: str) -> datetime:
    """
    Converts a date string in "dd-MM-yyyy" format to a datetime object.
    Raises an exception if the format is invalid.
    """
    try:
        return datetime.strptime(date_str, "%d-%m-%Y")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid date format: {date_str}. Please use dd-MM-yyyy."
        )
    
def fetch_sales_orders(query: dict) -> List[dict]:
    """
    Fetches sales orders from MongoDB based on the query.

    Args:
        query (dict): MongoDB query dictionary.

    Returns:
        List[dict]: List of sales orders retrieved from the database.
    """
    try:
        # Get the collection
        collection = get_salesOrder_collection()

        # Execute the query
        logger.debug(f"Executing MongoDB query: {query}")
        results = list(collection.find(query))

        logger.info(f"Retrieved {len(results)} records from MongoDB.")
        return results
    except Exception as e:
        logger.error(f"Error querying MongoDB: {e}", exc_info=True)
        raise    

def serialize_document(order: dict):
    if isinstance(order["_id"], ObjectId):
        # Store the _id in salesOrderId for easier access
        order["salesOrderId"] = str(order["_id"])  # Convert ObjectId to string and store it in salesOrderId
        del order["_id"]  # Optionally remove the _id field, since it's now in salesOrderId
    
    # Convert deliveryDate to dd-mm-yyyy
    if order.get("deliveryDate"):
        order["deliveryDate"] = format_date_to_ddmmyyyy(order["deliveryDate"])
    
    return order


def format_date_to_ddmmyyyy(date: datetime) -> str:
    return date.strftime("%d-%m-%Y")

@router.post("/", response_model=str)
async def create_salesOrder(salesOrder: SalesOrderPost):
    # Convert the incoming deliveryDate to datetime object
    delivery_data = convert_to_date(salesOrder.deliveryDate)
    # order_date = datetime.now() if not salesOrder.orderDate else convert_to_date(salesOrder.orderDate)

    # Prepare the new sales order data for insertion
    new_salesOrder_data = {**salesOrder.dict(), "deliveryDate": delivery_data}

    # Insert into MongoDB
    result = get_salesOrder_collection().insert_one(new_salesOrder_data)
    return str(result.inserted_id)


@router.get("/")
async def get_sales_orders(
    deliveryStartDate: Optional[str] = Query(None),
    deliveryEndDate: Optional[str] = Query(None),
    deliveryDate: Optional[str] = Query(None),
    customerNumber: Optional[str] = None,
    customerName: Optional[str] = None,
    orderDate: Optional[str] = None,
    paymentType: Optional[str] = None,
    minAdvanceAmount: Optional[float] = None,
    salesOrderLast5Digits: Optional[str] = None,
    filterCreditCustomer: Optional[bool] = Query(False, alias="filter-credit-customer"),
    filterCreditCustomerPreinvoice: Optional[bool] = Query(False, alias="filter-credit-customer-preinvoice")
):
    """
    Fetch sales orders based on query parameters.
    """
    try:
        # Log incoming request parameters
        logger.info("Received request to fetch sales orders.")
        logger.info(f"Input parameters: deliveryStartDate={deliveryStartDate}, deliveryEndDate={deliveryEndDate}, "
                    f"customerNumber={customerNumber}, customerName={customerName}, orderDate={orderDate}, "
                    f"paymentType={paymentType}, minAdvanceAmount={minAdvanceAmount}, salesOrderLast5Digits={salesOrderLast5Digits}")

        # Initialize the query object
        query = {}
        logger.debug(f"Initial query: {query}")

        # Parse date filters
        if deliveryStartDate and deliveryEndDate:
            start_date = datetime.strptime(deliveryStartDate, "%d-%m-%Y")
            end_date = datetime.strptime(deliveryEndDate, "%d-%m-%Y")
            end_date = end_date.replace(hour=23, minute=59, second=59)
            query["deliveryDate"] = {"$gte": start_date, "$lte": end_date}
            logger.debug(f"Updated query with deliveryDate filter: {query}")
        elif deliveryDate:
            specific_date = datetime.strptime(deliveryDate, "%d-%m-%Y")
            query["deliveryDate"] = specific_date
            logger.debug(f"Updated query with specific deliveryDate filter: {query}")

        # Apply customer filters
        if customerName:
            query["customerName"] = {"$regex": customerName, "$options": "i"}
            logger.debug(f"Updated query with customerName filter: {query}")

        if customerNumber:
            query["customerNumber"] = {"$regex": customerNumber, "$options": "i"}
            logger.debug(f"Updated query with customerNumber filter: {query}")

        # Apply salesOrderLast5Digits filter
        if salesOrderLast5Digits:
            logger.debug(f"Trying to apply filter for salesOrderLast5Digits: {salesOrderLast5Digits}")
            query["salesOrderId"] = {"$regex": f"{salesOrderLast5Digits}$", "$options": "i"}
            logger.debug(f"Updated query with salesOrderLast5Digits filter: {query}")
    
        # Apply credit customer filters BEFORE fetching data
        if filterCreditCustomer and filterCreditCustomerPreinvoice:
            # Fetch orders with either credit customer or pre-invoiced credit sales
            query["$or"] = [
                {"creditCustomerOrder": "yes"},
                {"creditCustomerOrder": "credit sales order pre invoiced"}
            ]
            logger.info("Applied filter for both credit customer and credit sales pre-invoiced.")
        elif filterCreditCustomer:
            query["creditCustomerOrder"] = "yes"
            logger.info("Applied filter for credit customer orders only.")
        elif filterCreditCustomerPreinvoice:
            query["creditCustomerOrder"] = "credit sales order pre invoiced"
            logger.info("Applied filter for credit customer pre-invoiced only.")

        # Final query to be used in the database query
        logger.debug(f"Final query: {query}")

        # Fetch sales orders from MongoDB
        raw_orders = fetch_sales_orders(query)
        logger.debug(f"Raw orders fetched from DB: {raw_orders}")

        if not raw_orders:
            logger.debug("No orders found based on the query.")

        # Serialize the fetched orders
        serialized_orders = [serialize_document(order) for order in raw_orders]
        logger.debug(f"Serialized orders: {serialized_orders}")

        # Return the serialized orders
        return serialized_orders

    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    
@router.get("/{salesOrder_id}", response_model=SalesOrder)
async def get_salesOrder_by_id(salesOrder_id: str):
    salesOrder = get_salesOrder_collection().find_one({"_id": ObjectId(salesOrder_id)})
    if salesOrder:
        salesOrder["salesOrderId"] = str(salesOrder["_id"])
        return SalesOrder(**salesOrder)
    else:
        raise HTTPException(status_code=404, detail="SalesOrder not found")


@router.patch("/{salesOrder_id}")
async def patch_salesOrder(salesOrder_id: str, salesOrder_patch: SalesOrderPost):
    existing_salesOrder = get_salesOrder_collection().find_one({"_id": ObjectId(salesOrder_id)})
    if not existing_salesOrder:
        raise HTTPException(status_code=404, detail="salesOrder not found")

    updated_fields = {key: value for key, value in salesOrder_patch.dict(exclude_unset=True).items() if value is not None}
    if updated_fields:
        result = get_salesOrder_collection().update_one({"_id": ObjectId(salesOrder_id)}, {"$set": updated_fields})
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update salesOrder")

    updated_salesOrder = get_salesOrder_collection().find_one({"_id": ObjectId(salesOrder_id)})
    updated_salesOrder["_id"] = str(updated_salesOrder["_id"])
    return updated_salesOrder

@router.delete("/{salesOrder_id}")
async def delete_salesOrder(salesOrder_id: str):
    result = get_salesOrder_collection().delete_one({"_id": ObjectId(salesOrder_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="salesOrder not found")
    return {"message": "salesOrder deleted successfully"}


@router.get("/filter-by-order-date-today/", response_model=List[SalesOrder])
async def filter_by_order_date_today():
    # Get the current date in dd-MM-yyyy format
    current_date = datetime.now().strftime("%d-%m-%Y")
    print(f"Current date for filtering: {current_date}")

    # Construct MongoDB query to match orders with today's orderDate
    query = {"orderDate": {"$eq": current_date}}
    print(f"Query for filtering: {query}")

    # Retrieve orders from MongoDB
    salesOrders = list(get_salesOrder_collection().find(query))
    print(f"Sales Orders fetched: {salesOrders}")

    if not salesOrders:
        print("No orders found for today.")
        raise HTTPException(status_code=404, detail="No orders found for today.")

    # Add salesOrderId and convert to response model
    result = []
    for salesOrder in salesOrders:
        salesOrder["salesOrderId"] = str(salesOrder["_id"])
        print(f"Processed Sales Order: {salesOrder}")
        result.append(SalesOrder(**salesOrder))

    return result

@router.get("/soadvancedtotalcash", response_model=List[SalesOrder])
async def get_sales_orders(
   
    orderDate: Optional[str] = None,
    paymentType: Optional[str] = None,
    minAdvanceAmount: Optional[float] = None,
):
    """
    Retrieve sales orders based on customerNumber, customerName, deliveryDate, orderDate,
    paymentType, and advanceAmount.
    
    """
    # Build the query dynamically based on the provided filters
    query = {}
    
    if orderDate:
        query["orderDate"] = orderDate
    if paymentType:
        query["paymentType"] = paymentType
    if minAdvanceAmount is not None:
        query["advanceAmount"] = {"$gt": minAdvanceAmount}  # Greater than specified advanceAmount

    # Log the query for debugging
    logging.info(f"Executing query: {query}")

    # Fetch sales orders matching the query
    salesOrders = list(get_salesOrder_collection().find(query))

    if not salesOrders:
        raise HTTPException(status_code=404, detail="No sales orders found for the given criteria.")

    # Format the response
    formatted_salesOrders = [
        SalesOrder(**{**order, "salesOrderId": str(order["_id"])}) for order in salesOrders
    ]

    return formatted_salesOrders

@router.patch("/create_invoice/{salesOrder_id}")
def create_invoice_from_sales_order(salesOrder_id: str):
    try:
        # Fetch the sales order (sync)
        sales_order_collection = get_salesOrder_collection()
        sales_order = sales_order_collection.find_one({"_id": ObjectId(salesOrder_id)})

        if not sales_order:
            raise HTTPException(status_code=404, detail="Sales Order not found")

        # Map sales order data to invoice model
        invoice_data = Invoice(
            itemName=sales_order.get("itemName"),
            price=sales_order.get("price"),
            weight=sales_order.get("weight"),
            qty=sales_order.get("qty"),
            amount=sales_order.get("amount"),
            tax=sales_order.get("tax"),
            uom=sales_order.get("uom"),
            totalAmount=sales_order.get("totalAmount"),
            totalAmount2=sales_order.get("totalAmount2"),
            totalAmount3=sales_order.get("totalAmount"),
            status="Invoiced",
            salesType=sales_order.get("salesType"),
            customerPhoneNumber=sales_order.get("customerPhoneNumber", "No Number"),
            employeeName=sales_order.get("employeeName"),
            branchId=sales_order.get("branchId"),
            branchName=sales_order.get("branchName"),
            paymentType=sales_order.get("paymentType"),
            cash=sales_order.get("cash"),
            card=sales_order.get("card"),
            upi=sales_order.get("upi"),
            others=sales_order.get("others"),
            invoiceDate=datetime.now().strftime("%d-%m-%Y"),
            invoiceTime=datetime.now().strftime("%H:%M:%S"),
            shiftNumber=sales_order.get("shiftNumber"),
            shiftId=sales_order.get("shiftId"),
            invoiceNo="INV" + str(ObjectId()),  # Generate Invoice Number
            customCharge=sales_order.get("customCharge"),
            discountAmount=sales_order.get("discountAmount"),
            discountPercentage=sales_order.get("discountPercentage"),
            user=sales_order.get("user"),
        )

        # Insert the invoice data into the invoice collection (sync)
        invoice_collection = get_invoice_collection()
        invoice_result = invoice_collection.insert_one(invoice_data.dict())

        # Update the status of the sales order (sync)
        update_result = sales_order_collection.update_one(
            {"_id": ObjectId(salesOrder_id)},
            {"$set": {"status": "SalesOrder Completed",  # Update status to "Invoiced"
                    "invoiceDate": datetime.now().strftime("%d-%m-%Y")}}
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update the sales order status")

        return {"message": "Sales Order status updated and Invoice created successfully", "invoiceId": str(invoice_result.inserted_id)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")
    
    
    
    
    
    
    
@router.patch("/crsopreinvoice/")
async def patch_multiple_credit_sales_orders_pre_invoiced(salesOrder_ids: List[str]):
        """
        Updates multiple sales orders to set `creditCustomerOrder` to
        "credit sales order pre invoiced".

        Args:
            salesOrder_ids (List[str]): The list of sales order IDs to update.

        Returns:
            dict: The updated sales orders or an error message if not found.
        """
        try:
            updated_sales_orders = []
            for salesOrder_id in salesOrder_ids:
                # Validate and convert the salesOrder_id to ObjectId
                try:
                    object_id = ObjectId(salesOrder_id)
                except InvalidId as e:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid salesOrder_id: {e}"
                    )

                # Find the sales order by ID
                existing_sales_order = get_salesOrder_collection().find_one({"_id": object_id})
                if not existing_sales_order:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Sales order not found for ID: {salesOrder_id}"
                    )

                # Update the sales order
                update_data = {
                    "$set": {
                        "creditCustomerOrder": "credit sales order pre invoiced"
                    }
                }
                result = get_salesOrder_collection().update_one({"_id": object_id}, update_data)

                if result.modified_count == 0:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to update the sales order for ID: {salesOrder_id}"
                    )

                # Fetch the updated sales order
                updated_sales_order = get_salesOrder_collection().find_one({"_id": object_id})
                updated_sales_order["_id"] = str(updated_sales_order["_id"])  # Convert ObjectId to string
                updated_sales_orders.append(updated_sales_order)

            return {
                "message": "Sales orders updated successfully",
                "salesOrders": updated_sales_orders
            }

        except Exception as e:
            logger.error(f"Error during update: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal Server Error")

@router.patch("/crsoinvoice/")
async def patch_multiple_credit_sales_orders_pre_invoiced(salesOrder_ids: List[str]):
        """
        Updates multiple sales orders to set `creditCustomerOrder` to
        "credit sales order pre invoiced".

        Args:
            salesOrder_ids (List[str]): The list of sales order IDs to update.

        Returns:
            dict: The updated sales orders or an error message if not found.
            
        """
        try:
            updated_sales_orders = []
            for salesOrder_id in salesOrder_ids:
                # Validate and convert the salesOrder_id to ObjectId
                try:
                    object_id = ObjectId(salesOrder_id)
                except InvalidId as e:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid salesOrder_id: {e}"
                    )

                # Find the sales order by ID
                existing_sales_order = get_salesOrder_collection().find_one({"_id": object_id})
                if not existing_sales_order:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Sales order not found for ID: {salesOrder_id}"
                    )

                # Update the sales order
                update_data = {
                    "$set": {
                        "creditCustomerOrder": "credit sales order invoiced"
                    }
                }
                result = get_salesOrder_collection().update_one({"_id": object_id}, update_data)

                if result.modified_count == 0:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to update the sales order for ID: {salesOrder_id}"
                    )

                # Fetch the updated sales order
                updated_sales_order = get_salesOrder_collection().find_one({"_id": object_id})
                updated_sales_order["_id"] = str(updated_sales_order["_id"])  # Convert ObjectId to string
                updated_sales_orders.append(updated_sales_order)

            return {
                "message": "Sales orders updated successfully",
                "salesOrders": updated_sales_orders
            }

        except Exception as e:
            logger.error(f"Error during update: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal Server Error")    
    

