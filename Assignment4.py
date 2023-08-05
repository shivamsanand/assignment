from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pymongo import MongoClient
from pydantic import BaseModel

#2.	GET method – get registered user details
#Hint : Unique user_id for both database 

# PostgreSQL database configuration
DATABASE_URL = "postgresql://username:password@localhost/dbname"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# MongoDB configuration
MONGODB_URL = "mongodb://localhost:27017/"
mongo_client = MongoClient(MONGODB_URL)
mongo_db = mongo_client["profile_db"]
mongo_collection = mongo_db["profiles"]

app = FastAPI()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    phone = Column(String, unique=True, index=True)

class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str
    phone: str
    profile_picture: str = None

class UserCheck(BaseModel):
    email: str
    phone: str

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str
    profile_picture: str = None

@app.post("/register/", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(SessionLocal)):
    # Same registration code as before
    # ...

@app.post("/check/", response_model=UserResponse)
def check_user(user: UserCheck, db: Session = Depends(SessionLocal)):
    # Same checking code as before
    # ...

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(SessionLocal)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Fetch profile picture from MongoDB
    profile_data = mongo_collection.find_one({"user_id": user.id})
    profile_picture = profile_data["profile_picture"] if profile_data else None

    return UserResponse(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        profile_picture=profile_picture,
    )
