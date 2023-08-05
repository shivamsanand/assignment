from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

#1. Write a program for user registration in fastAPI ( Using postgreSQL )
#a. Registration fields – Full Name,Email,Password,Phone,Profile_picture
#b. Create table Users to store : First Name,Password,Email,Phone
#c. Create table Profile to store : Profile_picture
#d. Check Email , Phone already exist


DATABASE_URL = "postgresql://username:password@localhost/dbname"

app = FastAPI()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    phone = Column(String, unique=True, index=True)

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    profile_picture = Column(String)

Base.metadata.create_all(bind=engine)

class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str
    phone: str
    profile_picture: str = None

class UserCheck(BaseModel):
    email: str
    phone: str

@app.post("/register/", response_model=User)
def register_user(user: UserCreate, db: Session = Depends(SessionLocal)):
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    existing_phone = db.query(User).filter(User.phone == user.phone).first()
    if existing_phone:
        raise HTTPException(status_code=400, detail="Phone already exists")

    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/check/", response_model=User)
def check_user(user: UserCheck, db: Session = Depends(SessionLocal)):
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        return existing_email
    existing_phone = db.query(User).filter(User.phone == user.phone).first()
    if existing_phone:
        return existing_phone
    raise HTTPException(status_code=404, detail="User not found")
