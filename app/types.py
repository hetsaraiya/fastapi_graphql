import strawberry
import strawberry.quart 
from .database import get_db
from fastapi import Depends
from sqlalchemy.orm.session import Session
from . import models
from .hashing import Hash
from .schema import AccType, AccountInput as AccInp
from typing import Optional

@strawberry.type
class User:
    id: Optional[int]
    name: str
    phone: str
    profile_url: str
    email: str
    address: str

@strawberry.type
class Bank:
    id:int
    name:str
    interest_rates: float

@strawberry.input
class BankInput:
    id:int
    name:str
    interest_rates: float

@strawberry.input
class UserInput:
    name: str
    phone: int
    profile_url: str
    email: str
    password: str
    address: str

@strawberry.input
class AccountInput:
    id: Optional[int]
    user_id: int
    bank_id: int
    amount: int
    acc_type: str

@strawberry.type
class Account:
    id: Optional[int]
    user_id: int
    bank_id: int
    amount: Optional[int]
    acc_type: str

@strawberry.input
class UpdateAccountInput:
    id: int
    amount: Optional[int] = None
    acc_type: Optional[AccType] = None

@strawberry.input
class UpdateUser:
    id:int
    name: Optional[str] = None
    phone: Optional[int] = None
    profile_url: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    address: Optional[str] = None

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
    amount: Optional[int]
    acc_type: str

@strawberry.type
class Query:
    @strawberry.field
    def user(self, id: int) -> User:
        db = next(get_db())
        db_user = db.query(models.User).filter(models.User.id == id).first()
        db.close()
        
        if db_user is None:
            raise Exception("User not found")
        
        
        return User(
            id=db_user.id,
            name=db_user.name,
            phone=db_user.phone,
            profile_url=db_user.profile_url,
            email=db_user.email,
            address=db_user.address
        )
    
    @strawberry.field
    def bank(self, id:int) -> Bank:
        db = next(get_db())

        banks = db.query(models.Bank).filter(models.Bank.id == id).first()

        db.close()
        if not banks:
            raise Exception("Bank not found")

        return Bank(
            id=banks.id,
            name=banks.name,
            interest_rates=banks.interest_rates
        )
    
    @strawberry.field
    def account() -> list[AccOutput]:
        db = next(get_db())

        all_acc = db.query(models.Account).all()

        db.close()
        return [
            AccOutput(
                id=acc.id,
                user=db.query(models.User).filter(models.User.id == acc.user_id).first(),
                bank=db.query(models.Bank).filter(models.Bank.id == acc.bank_id).first(),
                amount=acc.amount,
                acc_type=acc.acc_type
            )
            for acc in all_acc
        ]


    @strawberry.field
    def all_users() -> list[User]:
        db = next(get_db())
        users = db.query(models.User).all()
        return [
            User(
                id=user.id,
                name=user.name,               
                phone=user.phone,
                profile_url=user.profile_url,
                email=user.email,
                address=user.address,
            )for user in users
        ]

    

@strawberry.type
class Mutation:

    @strawberry.mutation
    def bank(bank : BankInput) -> Bank:
        db = next(get_db())
        reg_bank = models.Bank(
            id= bank.id,
            name=bank.name,
            interest_rates=bank.interest_rates
        )
        
        db.add(reg_bank)
        db.commit()
        db.refresh(reg_bank)

        return Bank(
            id=reg_bank.id,
            name=reg_bank.name,
            interest_rates=reg_bank.interest_rates
        )
    
    @strawberry.mutation
    def user(user: UserInput) -> User:

        db = next(get_db())

        exist = db.query(models.User.email).filter(models.User.email == user.email or models.User.phone == user.phone).first()

        if exist is not None:
            raise Exception("User with email or phone already exists")
        hashed_pass = Hash.bcrypt(user.password)
        add_user = models.User(
            name=user.name,
            phone=user.phone,
            profile_url=user.profile_url,
            email=user.email,
            password=hashed_pass,
            address=user.address
        )

        db.add(add_user)
        db.commit()
        db.refresh(add_user)
        return User(
            id=add_user.id,
            name=add_user.name,
            phone=add_user.phone,
            profile_url=add_user.profile_url,
            email=add_user.email,
            address=add_user.address
        )
    
    @strawberry.mutation
    def create_account(acc: AccInp) -> Account:
        db = next(get_db())
        open_acc = models.Account(
            user_id=acc.user_id,
            bank_id=acc.bank_id,
            amount=acc.amount,
            acc_type=acc.acc_type.value
        )

        db.add(open_acc)
        db.commit()
        db.refresh(open_acc)

        db.close()
        return Account(
            id=open_acc.id,
            user_id=open_acc.user_id,
            bank_id=open_acc.bank_id,
            amount=open_acc.amount,
            acc_type=open_acc.acc_type
        )
    @strawberry.mutation
    def update_account(acc: UpdateAccountInput) -> Account:
        db = next(get_db())

        account = db.query(models.Account).filter(models.Account.id == acc.id).first()
        if acc.acc_type is not None and acc.amount is not None:
            account.acc_type = acc.acc_type.value if acc.acc_type is not None else account.acc_type
            account.amount = acc.amount if acc.amount is not None else account.amount
        else:
            db.delete(account)
            db.commit()
            return Account(
                id=account.id,
                user_id=account.user_id,
                bank_id=account.bank_id,
                amount=account.amount,
                acc_type=account.acc_type,
            )
        db.commit()
        db.refresh(account)

        return Account(
            id=account.id,
            user_id=account.user_id,
            bank_id=account.bank_id,
            amount=account.amount,
            acc_type=account.acc_type,
        )
    
    @strawberry.mutation
    def delete_bank(bank: int) -> Bank:
        db = next(get_db())
        bank = db.query(models.Bank).filter(models.Bank.id == bank).first()
        db.delete(bank)
        db.commit()
        return Bank(
            id=bank.id,
            name=bank.name,
            interest_rates=bank.interest_rates
        )

    @strawberry.mutation
    def delete_user(id: int) -> str:
        db = next(get_db())

        user = db.query(models.User).filter(models.User.id == id).first()
        db.delete(user)
        db.commit()
        return "Deleted"
    
    @strawberry.mutation
    def update_user(user: UpdateUser) -> User:

        db = next(get_db())
        user_found = db.query(models.User).filter(models.User.id == user.id).first()
        user_found.name = user.name if user.name is not None else user_found.name
        user_found.phone = user.phone if user.phone is not None else user_found.phone
        user_found.profile_url = user.profile_url if user.profile_url is not None else user_found.profile_url
        user_found.email = user.email if user.email is not None else user_found.email
        user_found.password = user.password if user.password is not None else user_found.password
        user_found.address = user.address if user.address is not None else user_found.address

        db.commit()

        return User(
            id=user_found.id,
            name = user_found.name,
            phone = user_found.phone,
            profile_url = user_found.profile_url,
            email = user_found.email,
            address = user_found.address,
        )

schema = strawberry.Schema(query=Query, mutation=Mutation)
