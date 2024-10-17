from jose import JWTError, jwt
from fastapi import HTTPException, status
from .types import User


from .token_gen import SECRET_KEY, ALGORITHM

def authorize(authorization: str) -> User | str:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No authorization token provided")

    try:
        token_type, token = authorization.split()
        if token_type != "Bearer":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id = payload.get("id")
        user_name = payload.get("name")
        user_phone = payload.get("phone")
        user_profile_url = payload.get("profile_url")
        user_email = payload.get("email")
        user_address = payload.get("address")

        return User(
            id=user_id,
            name=user_name,
            phone=user_phone,
            profile_url=user_profile_url,
            email=user_email,
            address=user_address
        )

    except JWTError as e:
        print(f"JWTError: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    except Exception as e:
        print(f"Error decoding token: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")



from strawberry.fastapi import BaseContext
from functools import cached_property

class Context(BaseContext):
    @cached_property
    def user(self) -> User | None:
        if not self.request:
            return None

        authorization = self.request.headers.get("Authorization", None)
        return authorize(authorization)
