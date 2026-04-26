import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from weather_app_python.settings import settings

# Import security and services
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

# Import the Bouncer and Vault
from weather_app_python.web.api.users.user_create import UserCreate
from weather_app_python.db.models.user import User

# Import database session dependency
from weather_app_python.db.dependencies import get_db_session

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# This tells FastAPI exactly where the frontend should go to get a token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")

router = APIRouter()

def get_password_hash(password: str) -> str:
    """Hashes a plain-text password using pure Bcrypt."""
    # 1. Convert the standard string into raw bytes
    pwd_bytes = password.encode('utf-8')
    # 2. Generate a random salt and hash the password
    hashed_bytes = bcrypt.hashpw(pwd_bytes, bcrypt.gensalt())
    # 3. Convert back to a standard string so PostgreSQL can save it
    return hashed_bytes.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks if a raw password matches the Bcrypt hash in the database."""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )

def create_access_token(data: dict) -> str:
    """Creates a cryptographically signed JWT passport."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/register")
async def register_user(
    user_data: UserCreate, 
    db: AsyncSession = Depends(get_db_session)
):
    # 1. The Bouncer: Search the database to see if the username is taken
    query = select(User).where(User.username == user_data.username)
    result = await db.execute(query)
    existing_user = result.scalars().first()

    if existing_user:
        # 2. Kick them out with a specific 400 error!
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken. Please choose another one."
        )

    # 3. If they pass the check, continue with your normal hash and save logic
    real_hashed_pwd = get_password_hash(user_data.password)
    
    # Create a new SQLAlchemy User model
    new_user = User(
        username=user_data.username,
        hashed_password=real_hashed_pwd 
    )
    
    # Add it to the vault and save
    db.add(new_user)
    await db.commit()
    
    return {"message": "User successfully created!", "username": new_user.username}

@router.post("/login")
async def login_for_access_token(
    # This magic dependency expects form data (username/password), not raw JSON
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db_session)
):
    # Step 1: Search the database for the user
    query = select(User).where(User.username == form_data.username)
    result = await db.execute(query)
    db_user = result.scalars().first()

    # Step 2: Reject if user doesn't exist OR password doesn't match
    if not db_user or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Step 3: Password is correct! Generate the JWT passport
    # We embed the `user_id` directly inside the signed token
    access_token = create_access_token(data={"sub": str(db_user.userid)})
    
    # Step 4: Return the token exactly how FastAPI expects it
    return {"access_token": access_token, "token_type": "bearer"}


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db_session)
):
    """The Security Guard: Checks the JWT and returns the logged-in user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Step 1: Decode the passport using our secret key
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        
        # Step 2: Extract the "sub" (Subject) which we know is the user_id
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
            
        # Convert string back to integer for the database
        token_user_id = int(user_id_str)
        
    except InvalidTokenError:
        # If the token is expired or forged by a hacker, kick them out!
        raise credentials_exception

    # Step 3: Check if the user actually still exists in the database
    query = select(User).where(User.userid == token_user_id)
    result = await db.execute(query)
    user = result.scalars().first()
    
    if user is None:
        raise credentials_exception
        
    # Step 4: Hand the fully verified User object into the endpoint
    return user