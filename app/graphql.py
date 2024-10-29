from .types import *
from .types import AccountInput as AccInp
from .token_gen import verify_token
from sqlalchemy.ext.asyncio import AsyncSession
from . import auth, models
from .hashing import Hash
from .database import get_db
from sqlalchemy.future import select
from fastapi import Depends
import json
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from .auth import Context
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")
from .decorators import require_authentication
from strawberry.exceptions import GraphQLError

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
    def qqq(info: strawberry.Info[Context]) -> str:
        # print(info.context.user.email)
        return "New"

    @strawberry.field
    @require_authentication
    async def user(self, info: strawberry.Info[Context]) -> User:
        try:
            async for db in get_db():
                result = await db.execute(
                    select(models.User).filter(models.User.email == info.context.user.email)
                )
                db_user = result.scalars().first()
                if db_user is None:
                    raise Exception("User not found")
                
                return User(    
                    id=db_user.id,
                    name=db_user.name,
                    phone=db_user.phone,
                    profile_url=db_user.profile_url,
                    email=db_user.email,
                    address=db_user.address,
                    is_deleted=db_user.is_deleted,
                    user_type=db_user.user_type.value,
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @strawberry.field
    @require_authentication
    async def account(self, info: strawberry.Info[Context]) -> list[AccOutput]:
        try:
            print("entered the account func")
            async for db in get_db():
                result = await db.execute(select(models.Account))
                all_acc = result.scalars().all()
                return [
                    AccOutput(
                        id=acc.id,
                        user=(await db.execute(select(models.User).filter(models.User.id == acc.user_id))).scalars().first(),
                        bank=(await db.execute(select(models.Bank).filter(models.Bank.id == acc.bank_id))).scalars().first(),
                        amount=acc.amount,
                        acc_type=acc.acc_type,
                        is_deleted=acc.is_deleted
                    )
                    for acc in all_acc
                ]
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    @strawberry.field
    @require_authentication
    async def id_account(self, id: int, info: strawberry.Info[Context]) -> AccOutput:
        print(id)
        try:
            async for db in get_db():
                result = await db.execute(select(models.Account).filter(models.Account.id == id))
                acc = result.scalars().first()
                return AccOutput(
                    id=acc.id,
                    user=(await db.execute(select(models.User).filter(models.User.id == acc.user_id))).scalars().first(),
                    bank=(await db.execute(select(models.Bank).filter(models.Bank.id == acc.bank_id))).scalars().first(),
                    amount=acc.amount,
                    acc_type=acc.acc_type,
                    is_deleted=acc.is_deleted
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @strawberry.field
    @require_authentication
    async def all_users(self, info: strawberry.Info[Context]) -> list[User]:
        try:
            async for db in get_db():
                result = await db.execute(select(models.User))
                users = result.scalars().all()
                return [
                    User(
                        id=user.id,
                        name=user.name,               
                        phone=user.phone,
                        profile_url=user.profile_url,
                        email=user.email,
                        address=user.address,
                        user_type=user.user_type.value,
                        is_deleted=user.is_deleted
                    ) for user in users
                ]
        except Exception as e:
            raise GraphQLError(str(e))
        
    @strawberry.field
    @require_authentication
    async def all_banks(self, info: strawberry.Info[Context]) -> list[Bank]:
        try:
            async for db in get_db():
                result = await db.execute(select(models.Bank))
                banks = result.scalars().all()
                return [
                    Bank(
                        id=bank.id,
                        name=bank.name,
                        interest_rates=bank.interest_rates,
                        is_deleted=bank.is_deleted
                    ) for bank in banks
                ]
        except Exception as e:
            raise GraphQLError(str(e))
        
    @strawberry.field
    @require_authentication
    async def id_bank(self, id: int, info: strawberry.Info[Context]) -> Bank:
        print(id)
        try:
            async for db in get_db():
                result = await db.execute(select(models.Bank).filter(models.Bank.id == id))
                bank = result.scalars().first()
                return Bank(
                    id=bank.id,
                    name=bank.name,
                    interest_rates=bank.interest_rates,
                    is_deleted=bank.is_deleted
                )
        except Exception as e:
            raise GraphQLError(str(e))




@strawberry.type
class Mutation:

    @strawberry.mutation
    @require_authentication
    async def bank(self, bank: BankInput, info: strawberry.Info[Context]) -> Bank:
        if info.context.user.user_type == "ADMIN":    
            try:
                async for db in get_db():
                    reg_bank = models.Bank(
                        id=bank.id,
                        name=bank.name,
                        interest_rates=bank.interest_rates
                    )
                    
                    db.add(reg_bank)
                    await db.commit()
                    await db.refresh(reg_bank)

                    return Bank(
                        id=reg_bank.id,
                        name=reg_bank.name,
                        interest_rates=reg_bank.interest_rates
                    )
            except Exception as e:
                raise GraphQLError( str(e))
        else:
            raise GraphQLError("Unauthorized")

    @strawberry.mutation
    async def create_user(self, userinp: UserInput, info: strawberry.Info[Context]) -> User:
        if True:
            try:
                async for db in get_db():
                    result = await db.execute(
                        select(models.User).filter((models.User.email == userinp.email) | (models.User.phone == userinp.phone))
                    )
                    exist = result.scalars().first()

                    if exist is not None and exist.is_deleted == False:
                        raise GraphQLError("User with email or phone already exists")
                    
                    hashed_pass = Hash.bcrypt(userinp.password)
                    add_user = models.User(
                        name=userinp.name,
                        phone=userinp.phone,
                        profile_url=userinp.profile_url,
                        email=userinp.email,
                        password=hashed_pass,
                        address=userinp.address,
                        created_at=datetime.now(),
                        user_type=userinp.user_type
                    )

                    db.add(add_user)
                    await db.commit()
                    await db.refresh(add_user)
                    return User(
                        id=add_user.id,
                        name=add_user.name,
                        phone=add_user.phone,
                        profile_url=add_user.profile_url,
                        email=add_user.email,
                        address=add_user.address
                    )
            except HTTPException as e:
                raise e
            except Exception as e:
                raise GraphQLError(str(e))
        else:
            raise GraphQLError("Unauthorized")

    @strawberry.mutation
    @require_authentication
    async def create_account(self, acc: AccInp, info: strawberry.Info[Context]) -> Account:
        if info.context.user.user_type == "ADMIN":   
            try:
                async for db in get_db():
                    open_acc = models.Account(
                        user_id=acc.user_id,
                        bank_id=acc.bank_id,
                        amount=acc.amount,
                        acc_type=acc.acc_type.value,
                        created_at=datetime.now(),
                        is_deleted=acc.is_deleted,
                    )

                    db.add(open_acc)
                    await db.commit()
                    await db.refresh(open_acc)
                    return Account(
                        id=open_acc.id,
                        user_id=open_acc.user_id,
                        bank_id=open_acc.bank_id,
                        amount=open_acc.amount,
                        acc_type=open_acc.acc_type,
                    )
            except Exception as e:
                raise GraphQLError(str(e))
        else:
            raise GraphQLError("Unauthorized")
        
    @strawberry.mutation
    @require_authentication
    async def update_account(self, acc: UpdateAccountInput, info: strawberry.Info[Context]) -> Account:
        if info.context.user.user_type == "ADMIN":
            try:
                async for db in get_db():
                    result = await db.execute(
                        select(models.Account).filter(models.Account.id == acc.id)
                    )
                    account = result.scalars().first()
                    if acc.acc_type is not None and acc.amount is not None:
                        account.acc_type = acc.acc_type.value if acc.acc_type is not None else account.acc_type
                        account.amount = acc.amount if acc.amount is not None else account.amount
                        account.updated_at = datetime.now()
                    else:
                        account.is_deleted = True
                        await db.commit()
                        await db.refresh(account)
                        return Account(
                            id=account.id,
                            user_id=account.user_id,
                            bank_id=account.bank_id,
                            amount=account.amount,
                            acc_type=account.acc_type,
                            updated_at=datetime.now()
                        )
                    await db.commit()
                    await db.refresh(account)

                    return Account(
                        id=account.id,
                        user_id=account.user_id,
                        bank_id=account.bank_id,
                        amount=account.amount,
                        acc_type=account.acc_type,
                    )
            except Exception as e:
                raise GraphQLError(str(e))
        else:
            raise GraphQLError("Unauthorized")
        
    @strawberry.mutation
    @require_authentication
    async def update_bank(self, bank: BankInput, info: strawberry.Info[Context]) -> Bank:
        if info.context.user.user_type == "ADMIN":
            try:
                async for db in get_db():
                    result = await db.execute(
                        select(models.Bank).filter(models.Bank.id == bank.id)
                    )
                    bank_found = result.scalars().first()

                    if bank_found:
                        bank_found.name = bank.name if bank.name is not None else bank_found.name
                        bank_found.interest_rates = bank.interest_rates if bank.interest_rates is not None else bank_found.interest_rates
                        bank_found.updated_at = datetime.now()
                        await db.commit()
                        await db.refresh(bank_found)

                        return Bank(
                            id=bank_found.id,
                            name=bank_found.name,
                            interest_rates=bank_found.interest_rates,
                        )
                    else:
                        raise HTTPException(status_code=404, detail="Bank not found")
            except Exception as e:
                raise GraphQLError(str(e))
        else:
            raise GraphQLError("Unauthorized")
    

    @strawberry.mutation
    @require_authentication
    async def delete_bank(self, bank: int, info: strawberry.Info[Context]) -> Bank:
        if info.context.user.user_type == "ADMIN":
            try:
                async for db in get_db():
                    result = await db.execute(
                        select(models.Bank).filter(models.Bank.id == bank)
                    )
                    bank = result.scalars().first()
                    bank.is_deleted = True
                    bank.updated_at = datetime.now()
                    await db.commit()
                    await db.refresh(bank)
                    return Bank(
                        id=bank.id,
                        name=bank.name,
                        interest_rates=bank.interest_rates,
                    )
            except Exception as e:
                raise GraphQLError( detail=str(e))
        else:
            raise GraphQLError("Unauthorized")

    @strawberry.mutation
    @require_authentication
    async def delete_user(self, id: int, info: strawberry.Info[Context]) -> str:
        if info.context.user.user_type == "ADMIN":
            try:
                async for db in get_db():
                    result = await db.execute(
                        select(models.User).filter(models.User.id == id)
                    )
                    user = result.scalars().first()
                    user.is_deleted = True
                    user.updated_at = datetime.now()
                    await db.commit()
                    await db.refresh(user)
                    return "Deleted"
            except Exception as e:
                raise GraphQLError(str(e))
        else:
            raise GraphQLError("Unauthorized")
    @strawberry.mutation
    async def update_user(self, user: UpdateUser, info: strawberry.Info[Context]) -> User:
        print(info.context.user)
        if info.context.user.user_type == "ADMIN":
            try:
                async for db in get_db():
                    async with db.begin():
                        result = await db.execute(
                            select(models.User).filter(models.User.id == user.id)
                        )
                        user_found = result.scalars().first()

                        if user_found:
                            user_found.name = user.name if user.name is not None else user_found.name
                            user_found.phone = user.phone if user.phone is not None else user_found.phone
                            user_found.profile_url = user.profile_url if user.profile_url is not None else user_found.profile_url
                            user_found.email = user.email if user.email is not None else user_found.email
                            user_found.password = Hash.bcrypt(user.password) if user.password is not None else user_found.password
                            user_found.address = user.address if user.address is not None else user_found.address
                            user_found.user_type = user.user_type if user.user_type is not None else user_found.user_type
                            user_found.updated_at = datetime.now()

                            # await db.commit()

                            return User(
                                id=user_found.id,
                                name=user_found.name,
                                phone=user_found.phone,
                                profile_url=user_found.profile_url,
                                email=user_found.email,
                                address=user_found.address,
                            )
                        else:
                            raise HTTPException(status_code=404, detail="User not found")
            except Exception as e:
                raise GraphQLError(str(e))
        else:
            raise GraphQLError("Unauthorized")
        
    @strawberry.mutation
    @require_authentication
    async def recover_user(self, id: int, info: strawberry.Info[Context]) -> str:
        if info.context.user.user_type == "ADMIN":
            try:
                async for db in get_db():
                    result = await db.execute(
                        select(models.User).filter(models.User.id == id)
                    )
                    user = result.scalars().first()
                    user.is_deleted = False
                    user.updated_at = datetime.now()
                    await db.commit()
                    await db.refresh(user)
                    return "Recovered"
            except Exception as e:
                raise GraphQLError(str(e))
        else:
            raise GraphQLError("Unauthorized")
        
    @strawberry.mutation
    @require_authentication
    async def recover_account(self, id: int, info: strawberry.Info[Context]) -> str:
        if info.context.user.user_type == "ADMIN":
            try:
                async for db in get_db():
                    result = await db.execute(
                        select(models.Account).filter(models.Account.id == id)
                    )
                    account = result.scalars().first()
                    account.is_deleted = False
                    account.updated_at = datetime.now()
                    await db.commit()
                    await db.refresh(account)
                    return "Recovered"
            except Exception as e:
                raise GraphQLError(str(e))
        else:
            raise GraphQLError("Unauthorized")
        
    @strawberry.mutation
    @require_authentication
    async def recover_bank(self, id: int, info: strawberry.Info[Context]) -> str:
        if info.context.user.user_type == "ADMIN":
            try:
                async for db in get_db():
                    result = await db.execute(
                        select(models.Bank).filter(models.Bank.id == id)
                    )
                    bank = result.scalars().first()
                    bank.is_deleted = False
                    bank.updated_at = datetime.now()
                    await db.commit()
                    await db.refresh(bank)
                    return "Recovered"
            except Exception as e:
                raise GraphQLError(str(e))
        else:
            raise GraphQLError("Unauthorized")

schema = strawberry.Schema(query=Query, mutation=Mutation)