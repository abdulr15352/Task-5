from passlib.context import CryptContext
from pydantic import SecretStr
from jose import JWTError, jwt, ExpiredSignatureError
from config import Settings
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from fastapi import Depends, HTTPException
from utils.constants import Endpoints, ResponseMessages
from datetime import datetime, timedelta, timezone
from db.DbConfig import get_db
from db.DbModels import UserDBModel
from sqlalchemy.orm import Session

settings = Settings()

admin_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def hash_context():
    return CryptContext(schemes=["bcrypt_sha256", "argon2", "scrypt", "pbkdf2_sha256"], deprecated="auto")

def hash_password(password: SecretStr) -> str:
    pwd_context = hash_context()
    secret = password.get_secret_value()
    return pwd_context.hash(secret)

def verify_password(plain_password: SecretStr, hashed_password: str) -> bool:
    pwd_context = hash_context()
    return pwd_context.verify(plain_password.get_secret_value(), hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    to_encode.update({"exp": int(expire.timestamp())})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY.get_secret_value(), algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=Endpoints.LOGIN)

def decode_access_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY.get_secret_value(), algorithms=[settings.JWT_ALGORITHM])
        email = payload.get("email")
        if email is None:
            raise HTTPException(status_code=401, detail=ResponseMessages.INVALID_TOKEN_MISSING_EMAIL)
        user = db.query(UserDBModel).filter(UserDBModel.email == email).first()
        if user is None or not user.is_active:
            raise HTTPException(status_code=401, detail=ResponseMessages.USER_NOT_FOUND)
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail=ResponseMessages.EXPIRED_TOKEN)
    except JWTError as e:
        raise HTTPException(status_code=401, detail=ResponseMessages.INVALID_TOKEN)

def verify_admin_token(api_key: str = Depends(admin_api_key_header)):
    if api_key != settings.ADMIN_API_TOKEN.get_secret_value():
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key
