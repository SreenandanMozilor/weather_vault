from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from weather_app_python.db.dependencies import get_db_session
from weather_app_python.web.api.users.schema import UserCreate, UserLogin, Token
from weather_app_python.db.dao.user_dao import UserDAO
from weather_app_python.services.auth import get_password_hash, verify_password, create_access_token

router = APIRouter()

@router.post("/register", response_model=Token)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db_session)
) -> Token:
    dao = UserDAO(db)
    
    exists_check = await dao.check_user_exists(user_data.username, user_data.email)
    if exists_check["exists"]:
        field = exists_check["field"].capitalize()
        raise HTTPException(status_code=400, detail=f"{field} is already taken.")

    hashed_pwd = get_password_hash(user_data.password)
    new_user = await dao.create_user_model(
        email=user_data.email,
        username=user_data.username, 
        hashed_password=hashed_pwd
    )
    await db.commit() 
    
    access_token = create_access_token(data={"sub": new_user.username})
    return Token(access_token=access_token, token_type="bearer")

@router.post("/login", response_model=Token)
async def login_for_access_token(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db_session)
) -> Token:
    dao = UserDAO(db)
    
    db_user = await dao.get_user_by_identifier(user_data.identifier)

    # ALIGNED: We check the plain text password against the securely named hashed_password column
    if not db_user or not verify_password(user_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": db_user.username})
    return Token(access_token=access_token, token_type="bearer")