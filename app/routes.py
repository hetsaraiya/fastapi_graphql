from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends
from . import database, models, token_gen as token
from . hashing import Hash
from sqlalchemy.orm.session import Session
from .schema import ShowUser, UserCreate
router = APIRouter(tags=["Auth"])


@router.post("login/")
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db) ):
    user = db.query(models.User).filter(
        models.User.email == request.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Invalid Credentials")
    if not Hash.verify(user.password, request.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Incorrect password")

    access_token = token.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

from app.hashing import Hash



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