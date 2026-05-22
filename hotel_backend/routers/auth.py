from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
import services.auth_service as auth_service
import services.employee_service as employee_service
from db import get_db
from models import Employee

router = APIRouter(prefix="/auth")

class Token(BaseModel):
    access_token: str
    token_type: str

class UserProfile(BaseModel):
    id: int
    username: str
    full_name: str
    position: str
    role: str

    model_config = ConfigDict(from_attributes=True)

class RegisterRequest(BaseModel):
    username: str
    full_name: str
    password: str
    position: str = "Front Desk"
    role: str = "receptionist"


class RegisterResponse(BaseModel):
    id: int
    username: str
    full_name: str
    position: str
    role: str

    model_config = ConfigDict(from_attributes=True)

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth_service.create_access_token(
        data={"sub": user.username, "role": user.role}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_user(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = auth_service.get_user_by_username(db, payload.username)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")

    hashed_password = auth_service.get_password_hash(payload.password)
    employee_id = employee_service.create_employee(db, payload, hashed_password)
    if not employee_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not create account")

    created_user = auth_service.get_user_by_username(db, payload.username)
    return created_user

@router.get("/me", response_model=UserProfile)
async def read_users_me(current_user: Employee = Depends(auth_service.get_current_active_employee)):
    return current_user
