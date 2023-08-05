from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship, joinedload
from pydantic import BaseModel


#GET method – get registered user details
#Hint : Unique user_id, Connect two tables (Users and Profile) using user_id as foreign key



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

    # Relationship to connect User and Profile tables using user_id as the foreign key
    profile = relationship("Profile", back_populates="user")

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    profile_picture = Column(String)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    # Relationship to connect User and Profile tables using user_id as the foreign key
    user = relationship("User", back_populates="profile")

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
    user = db.query(User).options(joinedload(User.profile)).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
