from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from . import database, models, token_gen as token
from .hashing import Hash
from .schema import ShowUser, UserCreate
import sqlalchemy
from fastapi.templating import Jinja2Templates
from fastapi import Request
router = APIRouter(tags=["Auth"])
from .token_gen import get_current_user

@router.post("/login/form")
async def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    query = sqlalchemy.select(models.User).where(models.User.email == request.username and models.User.is_deleted == False)
    result = await db.execute(query)
    user = result.scalars().first()
    print(user.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials 1",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not Hash.verify(user.password, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials 2",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = token.create_access_token(user=user)
    print({"access_token": access_token, "token_type": "bearer", "user_type": user.user_type.value})
    return {"access_token": access_token, "token_type": "bearer", "user_type": user.user_type.value}


templates = Jinja2Templates(directory="templates")

@router.get("/",)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/signup/", status_code=status.HTTP_201_CREATED)
def signup(request: UserCreate, db: Session = Depends(database.get_db)):
    
    existing_user = db.query(models.User).filter(models.User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    
    hashed_password = Hash.bcrypt(request.password)
    print(type(hashed_password))
    
    new_user = models.User(
        name=request.name,
        phone=request.phone,
        profile_url=request.profile_url,
        email=request.email,
        password=hashed_password,
        address=request.address
    )
    
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  

    return ShowUser(
        name= new_user.name,
        email= new_user.email,
        phone= new_user.phone
    )

@router.get("/login")
def login(request: Request, name: str = None, params: str = None):
    return templates.TemplateResponse("login.html", {
        "request": request,
        "name": name,
        "params": params
    })

@router.get("/api/")
def apis(request: Request, api :str = None):
    return templates.TemplateResponse(f"{api}.html", {"request": request})

@router.get("/profile")
def profile(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})

@router.get("/home")
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@router.get("/deposit")
def deposit(request: Request):
    return templates.TemplateResponse("deposit.html", {"request": request})

from pydantic import BaseModel
class DepositRequest(BaseModel):
    id: int
    amount: int

@router.post("/deposit/form")
async def deposit_form(request: Request, deposit: DepositRequest, db: Session = Depends(database.get_db)):
    id = deposit.id
    amount = deposit.amount
    print("id", id)
    print("amount", amount)
    query = sqlalchemy.select(models.Account).where(models.Account.id == id)
    result = await db.execute(query)
    account = result.scalars().first()
    account.amount += amount
    await db.commit()
    await db.refresh(account)
    return "done"

@router.get("/withdraw")
def withdraw(request: Request):
    return templates.TemplateResponse("withdraw.html", {"request": request})

@router.post("/withdraw/form")
async def withdraw_form(request: Request, deposit: DepositRequest, db: Session = Depends(database.get_db)):
    id = deposit.id
    amount = deposit.amount
    print("id", id)
    print("amount", amount)
    query = sqlalchemy.select(models.Account).where(models.Account.id == id)
    result = await db.execute(query)
    account = result.scalars().first()
    account.amount -= amount
    await db.commit()
    await db.refresh(account)
    return "done"

@router.get("/admin")
def admin(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})


@router.get("/admin2")
def admin(request: Request):
    return templates.TemplateResponse("admin2.html", {"request": request})