from fastapi import APIRouter, HTTPException,status
from typing import List
from bson import ObjectId
from fastapi.responses import HTMLResponse
from .models import Invoice, InvoiceCreate, InvoiceUpdate
from .utils import get_collection

router = APIRouter()
collection = get_collection('invoices')

# def serialize_dict(item) -> dict:
    
#     return {**{i: str(item[i]) for i in item if i == '_id'}, **{i: item[i] for i in item if i != '_id'}}

# @router.post('/', response_model=Invoice,status_code=status.HTTP_201_CREATED)
# async def create_invoices(invoice: InvoiceCreate):
#     invoice_dict = invoice.model_dump()
#     invoice_dict['invoiceId'] = str(ObjectId())
#     invoice_dict['status'] = 'active'  # Set default status to active
#     result = await collection.insert_one(invoice_dict)
#     if result.inserted_id:
#         return invoice_dict
#     raise HTTPException(status_code=500, detail="Error creating invoices invoice")

# @router.get('/', response_model=List[Invoice])
# async def get_invoices():
#     invoices = [serialize_dict(invoice) for invoice in await collection.find().to_list(1000)]
#     return invoices
    
# @router.get('/{invoice_id}', response_model=Invoice)
# async def get_invoices(invoice_id: str):
#     invoice = await collection.find_one({'invoiceId': invoice_id})
#     if invoice:
#         return serialize_dict(invoice)
#     raise HTTPException(status_code=404, detail="invoices invoice not found")

# @router.patch('/{invoice_id}', response_model=Invoice)
# async def update_invoices(invoice_id: str, invoice: InvoiceUpdate):
#     print(f"Updating invoices invoice with ID: {invoice_id}")  # Log the ID
#     result = await collection.update_one({'invoiceId': invoice_id}, {'$set': invoice.dict(exclude_unset=True)})
#     if result.modified_count == 1:
#         return serialize_dict(await collection.find_one({'invoiceId': invoice_id}))
#     raise HTTPException(status_code=404, detail="invoices invoice not found")

# @router.patch('/deactivate/{invoice_id}', response_model=Invoice)
# async def deactivate_invoices(invoice_id: str):
#     print(f"Deactivating invoices invoice with ID: {invoice_id}")  # Log the ID
#     result = await collection.update_one({'invoiceId': invoice_id}, {'$set': {'status': 'inactive'}})
#     if result.modified_count == 1:
#         return serialize_dict(await collection.find_one({'invoiceId': invoice_id}))
#     raise HTTPException(status_code=404, detail="invoices invoice not found")

# @router.patch('/activate/{invoice_id}', response_model=Invoice)
# async def activate_invoices(invoice_id: str):
#     result = await collection.update_one({'invoiceId': invoice_id}, {'$set': {'status': 'active'}})
#     if result.modified_count == 1:
#         return serialize_dict(await collection.find_one({'invoiceId': invoice_id}))
#     raise HTTPException(status_code=404, detail="invoices invoice not found")

# @router.delete('/{invoice_id}')
# async def delete_invoices(invoice_id: str):
#     result = await collection.delete_one({'invoiceId': invoice_id})
#     if result.deleted_count == 1:
#         return {"message": "invoices invoice deleted"}
#     raise HTTPException(status_code=404, detail="invoices invoice not found")





def serialize_dict(item) -> dict:
    return {**{i: str(item[i]) for i in item if i == '_id'}, **{i: item[i] for i in item if i != '_id'}}

def generate_html_invoice(invoice):
    # HTML template with embedded CSS for better styling
    return f"""
    <html>
        <head>
            <title>Best Mummy Sweets & Cakes</title>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    margin: 20px;
                    text-align: center;
                    background-color: #ffffff;
                    color: #000000;
                }}
                h1, h2, h3 {{
                    color: #000000;
                }}
                table {{
                    width: 80%;
                    border-collapse: collapse;
                    margin: 20px auto;
                    box-shadow: 0 2px 3px rgba(0,0,0,0.1);
                }}
                th, td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #000000;
                }}
                th {{
                    background-color: #000000;
                    color: white;
                }}
                tr:nth-child(even) {{
                    background-color: #f2f2f2;
                }}
                tr:hover {{
                    background-color: #f5f5f5;
                }}
                .total {{
                    font-weight: bold;
                   
                    color: black;
                }}
                .info-table {{
                    margin-bottom: 20px;
                }}
                .info-table td {{
                    padding: 8px;
                }}
            </style>
        </head>
        <body>
            <h1>Best Mummy Sweets & Cakes</h1>
            <table class="info-table">
                <tr>
                    <td>Date: {invoice['invoiceDate']}</td>
                    <td>Time: {invoice['invoiceTime']}</td>
                </tr>
                <tr>
                    <td>Branch: {invoice['branchName']}</td>
                    <td>ID: {invoice['branchId']}</td>
                </tr>
            </table>
            <table border="1">
                <tr>
                    <th>Item</th>
                    <th>Quantity</th>
                    <th>Unit Price</th>
                    <th>Amount</th>
                </tr>
                {"".join(f"<tr><td>{name}</td><td>{qty}</td><td>{price}</td><td>{amount}</td></tr>" for name, qty, price, amount in zip(invoice['itemName'], invoice['qty'], invoice['price'], invoice['amount']))}
                <tr class="total"><td colspan="3">Total Amount</td><td>{invoice['totalAmount']}</td></tr>
            </table>
            <p>Thank you for your business</p>
        </body>
    </html>
    """


@router.get('/{invoice_id}', response_class=HTMLResponse)
async def get_invoice(invoice_id: str):
    invoice = await collection.find_one({'invoiceId': invoice_id})
    if invoice:
        return generate_html_invoice(serialize_dict(invoice))
    raise HTTPException(status_code=404, detail="Invoice not found")