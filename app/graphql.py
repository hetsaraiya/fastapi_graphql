from .types import *
from .types import AccountInput as AccInp
from .token_gen import verify_token
from sqlalchemy.orm.session import Session
from . import auth, models
from .hashing import Hash
from .database import get_db

from fastapi import Depends
import json
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from .auth import Context
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")
from .decorators import require_authentication


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_token(token, credentials_exception)

@strawberry.type
class Query:

    @strawberry.field
    @require_authentication
    def qqq(info: strawberry.Info[Context]) -> str:
        print(info.context.user.email)
        return "New"


    @strawberry.field
    @require_authentication
    async def user(self, info: strawberry.Info[Context]) -> User:
        
        try:
            db = next(get_db())
            db_user = await db.query(models.User).filter(models.User.email == info.context.user.email).first()
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
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally: await db.close()

    @strawberry.mutation
    def bank(bank: BankInput, info: strawberry.Info[Context]) -> Bank:
    
        with get_db() as db:  
            try:
                reg_bank = Bank(
                    id=bank.id,
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
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
    
    @strawberry.field
    @require_authentication
    async def account(info: strawberry.Info[Context]) -> list[AccOutput]:
        try:
            db =  next(get_db())

            all_acc = await db.query(models.Account).all()
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
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @strawberry.field
    @require_authentication
    def all_users(info: strawberry.Info[Context]) -> list[User]:
        
        try:
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
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            db.close()

    

@strawberry.type
class Mutation:

    @strawberry.mutation
    @require_authentication
    def bank(bank : BankInput, info: strawberry.Info[Context]) -> Bank:
        
        # we can check if user is admin or authorized to perform this action or not 
        try:
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
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            db.close()
    
    @strawberry.mutation
    @require_authentication
    def user(user: UserInput, info: strawberry.Info[Context]) -> User:
        
        try:
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
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            db.close()
    
    @strawberry.mutation
    @require_authentication
    def create_account(acc: AccInp, info: strawberry.Info[Context]) -> Account:
        
        try:
            db = next(get_db())
            open_acc = models.Account(
                user_id=acc.user_id,
                bank_id=acc.bank_id,
                amount=acc.amount,
                acc_type=acc.acc_type.value,
                created_at=datetime.now(),
                # updated_at=acc.updated_at,
                is_deleted=acc.is_deleted,
            )

            db.add(open_acc)
            db.commit()
            db.refresh(open_acc)
            return Account(
                id=open_acc.id,
                user_id=open_acc.user_id,
                bank_id=open_acc.bank_id,
                amount=open_acc.amount,
                acc_type=open_acc.acc_type,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally: db.close()

    @strawberry.mutation
    @require_authentication
    def update_account(acc: UpdateAccountInput, info: strawberry.Info[Context]) -> Account:
        
        try:
            db = next(get_db())

            account = db.query(models.Account).filter(models.Account.id == acc.id).first()
            if acc.acc_type is not None and acc.amount is not None:
                account.acc_type = acc.acc_type.value if acc.acc_type is not None else account.acc_type
                account.amount = acc.amount if acc.amount is not None else account.amount
                account.updated_at=datetime.now()
            else:
                account.is_deleted =True
                db.commit()
                db.refresh(account)
                return Account(
                    id=account.id,
                    user_id=account.user_id,
                    bank_id=account.bank_id,
                    amount=account.amount,
                    acc_type=account.acc_type,
                    updated_at=datetime.now()
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
        except Exception as e: raise HTTPException(status_code=500, detail=str(e))
        finally: db.close()
    
    @strawberry.mutation
    @require_authentication
    def delete_bank(bank: int, info: strawberry.Info[Context]) -> Bank:
        
        try:
            db = next(get_db())
            bank = db.query(models.Bank).filter(models.Bank.id == bank).first()
            bank.is_deleted = True
            bank.updated_at=datetime.now()
            db.commit()
            db.refresh(bank)
            return Bank(
                id=bank.id,
                name=bank.name,
                interest_rates=bank.interest_rates,
            )
        except Exception as e: raise HTTPException(status_code=500, detail=str(e))
        finally: db.close()

    @strawberry.mutation
    @require_authentication
    def delete_user(id: int, info: strawberry.Info[Context]) -> str:
        
        try:
            db = next(get_db())

            user = db.query(models.User).filter(models.User.id == id).first()
            user.is_deleted = True
            user.updated_at=datetime.now()
            db.commit()
            db.refresh(user)
            return "Deleted"
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally: db.close()
    
    @strawberry.mutation
    @require_authentication
    def update_user(user: UpdateUser, info: strawberry.Info[Context]) -> User:
        
        
        try:
            db = next(get_db())
            user_found = db.query(models.User).filter(models.User.id == user.id).first()
            user_found.name = user.name if user.name is not None else user_found.name
            user_found.phone = user.phone if user.phone is not None else user_found.phone
            user_found.profile_url = user.profile_url if user.profile_url is not None else user_found.profile_url
            user_found.email = user.email if user.email is not None else user_found.email
            user_found.password = Hash.bcrypt(user.password) if user.password is not None else user_found.password
            user_found.address = user.address if user.address is not None else user_found.address
            user_found.updated_at = datetime.now()

            db.commit()

            return User(
                id=user_found.id,
                name = user_found.name,
                phone = user_found.phone,
                profile_url = user_found.profile_url,
                email = user_found.email,
                address = user_found.address,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            db.close()

schema = strawberry.Schema(query=Query, mutation=Mutation)
