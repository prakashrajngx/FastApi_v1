from typing import List
from fastapi import APIRouter, HTTPException,status
from bson import ObjectId
from .models import Employee, EmployeePost
from .utils import get_employee_collection, convert_to_string_or_emptys,generate_custom_emp_id

router = APIRouter()

@router.post("/", response_model=str,status_code=status.HTTP_201_CREATED)
async def create_employee(employee: EmployeePost):
    try:
        employee_collection = get_employee_collection()
        new_employee = employee.dict()
        new_employee["empId"] = generate_custom_emp_id(employee_collection)
        result = employee_collection.insert_one(new_employee)
        new_employee["employeeId"] = str(result.inserted_id)
        return new_employee["empId"]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/", response_model=List[Employee])
async def get_all_employees():
    employees = list(get_employee_collection().find())
    formatted_employees = []
    for employee in employees:
        employee["_id"] = str(employee["_id"])
        employee["employeeId"] = employee["_id"]
        formatted_employees.append(Employee(**convert_to_string_or_emptys(employee)))
    return formatted_employees

@router.get("/{employeeId}", response_model=Employee)
async def get_employee_by_id(employeeId: str):
    employee = get_employee_collection().find_one({"_id": ObjectId(employeeId)})
    if employee:
        employee["_id"] = str(employee["_id"])
        employee["employeeId"] = employee["_id"]
        return Employee(**convert_to_string_or_emptys(employee))
    else:
        raise HTTPException(status_code=404, detail="Employee not found")

@router.patch("/{employeeId}")
async def update_employee(employeeId: str, employee: EmployeePost):
    updated_fields = employee.dict(exclude_unset=True)
    result = get_employee_collection().update_one(
        {"_id": ObjectId(employeeId)},
        {"$set": convert_to_string_or_emptys(updated_fields)}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee updated successfully"}

@router.delete("/{employeeId}")
async def delete_employee(employeeId: str):
    result = get_employee_collection().delete_one({"_id": ObjectId(employeeId)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee deleted successfully"}
