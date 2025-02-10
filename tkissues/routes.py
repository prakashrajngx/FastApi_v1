from fastapi import APIRouter, HTTPException,status
from bson import ObjectId
from typing import List
from .models import Issue, IssuePost
from .utils import get_issue_collection, convert_to_string_or_emptys

router = APIRouter()

@router.post("/", response_model=str,status_code=status.HTTP_201_CREATED)
async def create_issue(issue: IssuePost):
    new_issue = issue.dict()  # Convert Pydantic model to dictionary
    result = get_issue_collection().insert_one(new_issue)
    return str(result.inserted_id)

@router.get("/", response_model=List[Issue])
async def get_all_issues():
    issues = list(get_issue_collection().find())
    formatted_issues = []
    for issue in issues:
        issue["_id"] = str(issue["_id"])  # Convert ObjectId to string
        issue["issueId"] = issue["_id"]  # Ensure IssueId is set
        formatted_issues.append(Issue(**convert_to_string_or_emptys(issue)))
    return formatted_issues

@router.get("/{issueId}", response_model=Issue)
async def get_issue_by_id(issueId: str):
    issue = get_issue_collection().find_one({"_id": ObjectId(issueId)})
    if issue:
        issue["_id"] = str(issue["_id"])
        issue["issueId"] = issue["_id"]
        return Issue(**convert_to_string_or_emptys(issue))
    else:
        raise HTTPException(status_code=404, detail="Issue not found")

@router.patch("/{issueId}")
async def update_issue(issueId: str, issue: IssuePost):
    updated_fields = issue.dict(exclude_unset=True)
    result = get_issue_collection().update_one(
        {"_id": ObjectId(issueId)},
        {"$set": convert_to_string_or_emptys(updated_fields)}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Issue not found")
    return {"message": "Issue updated successfully"}

@router.delete("/{issueId}")
async def delete_issue(issueId: str):
    result = get_issue_collection().delete_one({"_id": ObjectId(issueId)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Issue not found")
    return {"message": "Issue deleted successfully"}

@router.patch("/{issueId}/deactivate")
async def deactivate_issue(issueId: str):
    try:
        obj_id = ObjectId(issueId)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid issueId format: {issueId}") from e
    
    result = get_issue_collection().update_one(
        {"_id": obj_id},
        {"$set": {"status": "inactive"}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail=f"Issue with ID {issueId} not found")
    return {"message": "Issue deactivated successfully"}

@router.patch("/{issueId}/activate")
async def activate_issue(issueId: str):
    try:
        obj_id = ObjectId(issueId)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid issueId format: {issueId}") from e
    
    result = get_issue_collection().update_one(
        {"_id": obj_id},
        {"$set": {"status": "active"}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail=f"Issue with ID {issueId} not found")
    return {"message": "Issue activated successfully"}