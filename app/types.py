import strawberry
import strawberry.quart 
from .schema import AccType, AccountInput as AccInp
from typing import Optional, Any
from datetime import datetime

@strawberry.type
class User:
    id: Optional[int] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    profile_url: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    user_type: Optional[str] = None
    


@strawberry.type
class Bank:
    id: Optional[int] = None
    name: Optional[str] = None
    interest_rates: Optional[float] = None
    

@strawberry.input
class BankInput:
    id:Optional[int] = None
    name: Optional[str] = None
    interest_rates: Optional[float] = None

@strawberry.input
class UserInput:
    id: Optional[int] = None
    name: Optional[str]
    phone: Optional[int]
    profile_url: Optional[str]
    email: Optional[str]
    password: Optional[str] = None
    address: Optional[str] = None
    user_type: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_deleted: Optional[bool] = None

@strawberry.input
class AccountInput:
    id: Optional[int]
    user_id: int
    bank_id: int
    amount: int
    acc_type: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_deleted: Optional[bool] = None



@strawberry.input
class UpdateAccountInput:
    id: int
    amount: Optional[int] = None
    acc_type: Optional[AccType] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_deleted: Optional[bool] = None

@strawberry.input
class UpdateUser:
    id:int
    name: Optional[str] = None
    phone: Optional[int] = None
    profile_url: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    address: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_deleted: Optional[bool] = None
    user_type: Optional[str] = None

@strawberry.type
class AccBank:
    id:Optional[int] = None
    name:Optional[str] = None
    interest_rates: Optional[float] = None

@strawberry.type
class AccUser:
    id: Optional[int] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    profile_url: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

@strawberry.type
class AccOutput:
    id: Optional[int]
    user: Optional[AccUser] = None
    bank: Optional[AccBank] = None
    amount: Optional[int] = None
    acc_type: Optional[str] = None
    

@strawberry.type
class Account:
    id: Optional[int] = None
    user_id: Optional[int] = None
    bank_id: Optional[int] = None
    amount: Optional[int] = None
    acc_type: Optional[str] = None
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_deleted: Optional[bool] = None

@strawberry.input
class AccountInput:
    user_id: int
    bank_id: int
    amount: int
    acc_type: AccType
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_deleted: Optional[bool] = False