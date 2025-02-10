from pydantic import BaseModel, Field
from typing import List, Optional, Union,Any

class Employee(BaseModel):
    employeeId: Optional[Union[str, int]] = None
    empId: Optional[Union[str, int]] = None
    employeeName: Optional[str] = None
    department: Optional[Union[str, int]] = None
    designation: Optional[str] = None
    email: Optional[str] = None
    phoneNumber: Optional[str] = None
    status: Optional[str] = None

class EmployeePost(BaseModel):
    empId: Optional[Union[str, int]] = None
    employeeName: Optional[str] = None  
    department: Optional[Union[str, int]] = None
    designation: Optional[str] = None
    designation: Optional[str] = None
    email: Optional[str] = None
    phoneNumber: Optional[str] = None
    status: Optional[str] = None
    
