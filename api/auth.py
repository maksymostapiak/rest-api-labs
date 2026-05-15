from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from security import (
    verify_password, get_password_hash, create_access_token,
    create_refresh_token, SECRET_KEY, ALGORITHM
)
from jose import jwt, JWTError

router = APIRouter(prefix="/auth", tags=["Auth"])

fake_users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": get_password_hash("secret"),
    }
}

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict or not verify_password(form_data.password, user_dict["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильний логін або пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user_dict["username"]})
    refresh_token = create_refresh_token(data={"sub": user_dict["username"]})
    
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token, 
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
async def refresh_access_token(body: RefreshTokenRequest):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Невалідний або прострочений refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(body.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    new_access_token = create_access_token(data={"sub": username})
    new_refresh_token = create_refresh_token(data={"sub": username})

    return {
        "access_token": new_access_token, 
        "refresh_token": new_refresh_token, 
        "token_type": "bearer"
    }