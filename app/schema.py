from pydantic import BaseModel, EmailStr
from enum import Enum

class AccType(Enum):
    savings = "savings"
    current = "current"

class User(BaseModel):
    name: str
    phone: int
    profile_url: str
    email: str
    address: str
    password: str

class Bank(BaseModel):
    name: str
    interest_rates: str

class Account(BaseModel):
    user: User
    bank: Bank
    amount: int
    acc_type: AccType

class ShowUser(BaseModel):
    name: str
    email: str
    phone: int

    class config():
        from_attributes = True

class ShowAccount(BaseModel):
    
    user: ShowUser
    bank: Bank

    class config():
        from_attributes = True

class UserCreate(BaseModel):
    name: str  
    phone: int  
    profile_url: str 
    email: EmailStr  
    password: str 
    address: str 

    class Config:
        from_attributes = True


import strawberry
from typing import Optional

@strawberry.input
class AccountInput:
    user_id: int
    bank_id: int
    amount: int
    acc_type: AccType