from bson import ObjectId
from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List, Optional
from .models import Sections, SectionsPost
from .utils import get_sessions_collection

router = APIRouter()

@router.post("/", response_model=Sections, status_code=status.HTTP_201_CREATED)
async def create_section(section: SectionsPost):
    section_dict = jsonable_encoder(section)
    new_section = get_sessions_collection().insert_one(section_dict)
    created_section = get_sessions_collection().find_one({"_id": new_section.inserted_id})
    return Sections(**created_section)

@router.get("/", response_model=List[Sections])
async def get_all_sections(branch_name: Optional[str] = None, alias_name: Optional[str] = None):
    query = {}
    if branch_name:
        query['sectionsName'] = branch_name
    if alias_name:
        query['aliasName'] = alias_name

    sections = list(get_sessions_collection().find(query))
    return [Sections(sectionsId=str(section["_id"]), **section) for section in sections]

@router.get("/{section_id}", response_model=Sections)
async def get_section_by_id(section_id: str):
    section = get_sessions_collection().find_one({"_id": ObjectId(section_id)})
    if section:
        section["sectionsId"] = str(section["_id"])
        return Sections(**section)
    else:
        raise HTTPException(status_code=404, detail="Section not found")

@router.patch("/{section_id}")
async def update_section(section_id: str, section_update: SectionsPost):
    update_data = {k: v for k, v in section_update.dict(exclude_unset=True).items() if v is not None}
    result = get_sessions_collection().update_one({"_id": ObjectId(section_id)}, {"$set": update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update section")

    updated_section = get_sessions_collection().find_one({"_id": ObjectId(section_id)})
    return Sections(**updated_section)

@router.delete("/{section_id}")
async def delete_section(section_id: str):
    result = get_sessions_collection().delete_one({"_id": ObjectId(section_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Section not found")
    return {"message": "Section deleted successfully"}
