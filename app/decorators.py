from functools import wraps
from fastapi import HTTPException, status

def require_authentication(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Retrieve the `info` argument, which is usually the last argument
        info = kwargs.get('info')
        
        if info is None or info.context.user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        
        # Call the original function if authenticated
        return func(*args, **kwargs)
    
    return wrapper
