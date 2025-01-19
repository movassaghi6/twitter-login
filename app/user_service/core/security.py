from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from ..core.settings import SECRET_KEY, ALGORITHM
from ..repository.User import UserRepo
from ..schemas.user import TokenData, UserSafe
import jwt
from jwt.exceptions import InvalidTokenError
from ..core.logger import setup_logging



# Set up logging
loggers = setup_logging()
logger = loggers['security']

# OAuth2PasswordBearer instance for handling token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class PasswordManager:
    def __init__(self):
        # CryptContext instance for password hashing and verification
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def hash_password(self, plain_password):
        pass


class TokenManager:
    def create_access_token(self, data: dict, expires_delta: timedelta | None = None) -> str:
        """
        Creates a JWT access token with an optional expiration time.

        Args:
            data : the data to encode in the JWT.
            expires_delta: the time duration until the token expires.
                        Defaults to 15 minutes if not provided.
        
        Returns:
            str: the encoded JWT access token.
        """
        to_encode = data.copy() # Copy data to avoid side effects
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        
        to_encode.update({"exp": expire})
        # Encode JWT with provided data, secret_key, and algorithm
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.info(f"Access token created for user: {data.get('sub')}")
        return encoded_jwt

    def decode_token(self, token: str) -> TokenData:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                logger.warning("Token validation failed: 'sub' claim missing")
                self._raise_invalid_credentials_exception()
            return TokenData(username=username)
        except InvalidTokenError:
            logger.warning("Token validation failed: Invalid token")
            self._raise_invalid_credentials_exception()

    def _raise_invalid_credentials_exception(self):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


class UserAuthService:
    def __init__(self, password_manager: PasswordManager, token_manager: TokenManager, user_repo: UserRepo):
        self.password_manager = password_manager
        self.token_manager = token_manager
        self.user_repo = user_repo

    async def authenticate_user(self, username: str, password: str):
        logger.info(f"Authenticating user: {username}")
        user = await self.user_repo.get_by_username(username)
        if not user:
            logger.warning(f"Authentication failed: User not found - {username}")
            return False
        if not self.password_manager.verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed: Invalid password for user - {username}")
            return False
        logger.info(f"Authentication successful for user: {username}")
        return user
    
    async def get_user_dep(self, token: str = Depends(oauth2_scheme)) -> UserSafe:
        token_data = self.token_manager.decode_token(token)
        user = await self.user_repo.get_by_username(token_data.username)
        if user is None:
            logger.warning(f"Token validation failed: User not found - {token_data.username}")
            self.token_manager._raise_invalid_credentials_exception()
        logger.info(f"Token validated successfully for user: {token_data.username}")
        return UserSafe(
            username=user.username,
            phone_number=user.phone_number,
            email=user.email
        )


# Create instances of PasswordManager, TokenManager, and UserDAO
password_manager = PasswordManager()
token_manager = TokenManager()
user_repo = UserRepo()

# Inject dependencies into UserAuthService
user_auth_service = UserAuthService(password_manager, token_manager, user_repo)


async def authenticate_user(username: str, password: str):
    return await user_auth_service.authenticate_user(username, password)


async def get_user_dep(current_user: UserSafe = Depends(user_auth_service.get_user_dep)):
    return current_user

