from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pymongo import MongoClient
from pydantic import BaseModel

#Write a program for user registration in FastAPI ( Using two database PostgreSQL and MobgoDB 
#a.	Registration fields – Full Name,Email,Password,Phone,Profile_picture
#b.	First Name,Password,Email,Phone — postgreSQL
#c.	Profile picture – MongoDB
#d.	Check Email already exist



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

@app.post("/register/")
def register_user(user: UserCreate, db: Session = Depends(SessionLocal)):
    # Check if the email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create the new user in PostgreSQL
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Store the profile picture in MongoDB
    profile_data = {"user_id": db_user.id, "profile_picture": user.profile_picture}
    mongo_collection.insert_one(profile_data)

    return db_user


