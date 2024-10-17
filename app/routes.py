from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from . import database, models, token_gen as token
from .hashing import Hash
from .schema import ShowUser, UserCreate
import sqlalchemy
router = APIRouter(tags=["Auth"])

@router.post("/login/")
async def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    query = sqlalchemy.select(models.User).where(models.User.email == request.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not Hash.verify(user.password, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",  # Keep error message generic for security reasons
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = token.create_access_token(user=user)
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