from typing import List
from fastapi import APIRouter, HTTPException,status
from bson import ObjectId
from .models import Ticket, TicketPost
from .utils import get_ticket_collection, convert_to_string_or_emptys, generate_next_ticket_number
import logging
router = APIRouter()


logger = logging.getLogger(__name__)

@router.post("/", response_model=str,status_code=status.HTTP_201_CREATED)
async def create_ticket(ticket: TicketPost):
    tickets_collection = get_ticket_collection()
    ticket_data = ticket.dict()
    ticket_data['ticketNo'] = generate_next_ticket_number(tickets_collection)
    result = tickets_collection.insert_one(ticket_data)
    logger.info(f"Ticket created with ID: {result.inserted_id}")
    return str(result.inserted_id)

@router.get("/", response_model=List[Ticket])
async def get_all_tickets():
    tickets = list(get_ticket_collection().find())
    return [Ticket(**convert_to_string_or_emptys(ticket)) for ticket in tickets]

@router.get("/{ticketId}", response_model=Ticket)
async def get_ticket_by_id(ticketId: str):
    if not ObjectId.is_valid(ticketId):
        raise HTTPException(status_code=400, detail="Invalid Ticket ID")

    ticket = get_ticket_collection().find_one({"_id": ObjectId(ticketId)})
    if ticket:
        return Ticket(**convert_to_string_or_emptys(ticket))
    else:
        raise HTTPException(status_code=404, detail="Ticket not found")

@router.patch("/{ticketId}")
async def update_ticket(ticketId: str, ticket: TicketPost):
    if not ObjectId.is_valid(ticketId):
        raise HTTPException(status_code=400, detail="Invalid Ticket ID")

    updated_fields = ticket.dict(exclude_unset=True)
    result = get_ticket_collection().update_one(
        {"_id": ObjectId(ticketId)},
        {"$set": convert_to_string_or_emptys(updated_fields)}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"message": "Ticket updated successfully"}

@router.delete("/{ticketId}")
async def delete_ticket(ticketId: str):
    if not ObjectId.is_valid(ticketId):
        raise HTTPException(status_code=400, detail="Invalid Ticket ID")

    result = get_ticket_collection().delete_one({"_id": ObjectId(ticketId)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"message": "Ticket deleted successfully"}

@router.patch("/{ticketId}/deactivate")
async def deactivate_ticket(ticketId: str):
    if not ObjectId.is_valid(ticketId):
        raise HTTPException(status_code=400, detail="Invalid Ticket ID")

    result = get_ticket_collection().update_one(
        {"_id": ObjectId(ticketId)},
        {"$set": {"status": "0"}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail=f"Ticket with ID {ticketId} not found")
    return {"message": "Ticket deactivated successfully"}

@router.patch("/{ticketId}/activate")
async def activate_ticket(ticketId: str):
    if not ObjectId.is_valid(ticketId):
        raise HTTPException(status_code=400, detail="Invalid Ticket ID")

    result = get_ticket_collection().update_one(
        {"_id": ObjectId(ticketId)},
        {"$set": {"status": "1"}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail=f"Ticket with ID {ticketId} not found")
    return {"message": "Ticket activated successfully"}
