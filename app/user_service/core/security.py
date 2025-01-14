from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from ..core.settings import SECRET_KEY, ALGORITHM
from ..db.database import mongo_db
from ..schemas.user import TokenData, UserSafe
import jwt
from jwt.exceptions import InvalidTokenError
from ..core.logger import setup_logging


# Set up logging
loggers = setup_logging()
logger = loggers['security']

# CryptContext instance for password hashing and verification
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2PasswordBearer instance for handling token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    """
    Verifies if the provided plain password matches the hashed password.

    Args:
        plain_password (str): The plain text password to verify.
        hashed_password (str): The hashed password to compare against.

    Returns:
        bool: True if the password is valid, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Creates a JWT access token with an optional expiration time.

    Args:
        data : the data to encode in the JWT.
        expires_delta: the time duration until the token expires.
                       Defaults to 15 minutes if not provided.
    
    Returns:
        str: the encoded JWT access token.
    """
    to_encode= data.copy() # Copy data to avoid side effects
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    # Encode JWT with provided data, secret_key, and algorithm
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"Access token created for user: {data.get('sub')}")
    return encoded_jwt


# Authenticate a user by verifying username and password
async def authenticate_user(username: str, password: str):
    logger.info(f"Authenticating user: {username}")
    user = await mongo_db.get_user_by_username(username=username)
    if not user:
        logger.warning(f"Authentication failed: User not found - {username}")
        return False
    if not verify_password(password, user.hashed_password):
        logger.warning(f"Authentication failed: Invalid password for user - {username}")
        return False
    logger.info(f"Authentication successful for user: {username}")
    return user


# Fetch the authenticated user based on the JWT token
async def get_user_dep(token: Annotated[UserSafe, Depends(oauth2_scheme)]):
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload= jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            logger.warning("Token validation failed: 'sub' claim missing")
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        logger.warning("Token validation failed: Invalid token")
        raise credentials_exception
    
    user = await mongo_db.get_user_by_username(token_data.username)
    if user is None:
        logger.warning(f"Token validation failed: User not found - {token_data.username}")
        raise credentials_exception
    logger.info(f"Token validated successfully for user: {token_data.username}")
    return UserSafe(
        username= user.username,
        phone_number= user.phone_number,
        email= user.email
    )


