from fastapi import FastAPI, Request, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from agents import graph


app = FastAPI()

server = 'DESKTOP-G5V0UP1\\SQLEXPRESS'
database = 'Log_File'
driver = 'ODBC+Driver+18+for+SQL+Server'

DATABASE_URL = f'mssql+pyodbc://@{server}/{database}?driver={driver}&trusted_connection=yes&Encrypt=no'

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# --- ORM Model (TABLE)---
class LOG_ENTRIES(Base):
    __tablename__ = "Log_Entries"
    id = Column(Integer, primary_key=True, index=True)
    Log = Column(String, nullable=False)
    Label = Column(String, nullable=False)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)

Base.metadata.create_all(bind=engine)


# --- Password Hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str):
    return pwd_context.hash(password)



# Input model for request body
class LogEntry(BaseModel):
    log: str


class UserLogin(BaseModel):
    username: str
    password: str



@app.post("/register")
def register(user: UserLogin):
    db = SessionLocal()
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Username already exists")
    hashed_pw = hash_password(user.password)
    db_user = User(username=user.username, password_hash=hashed_pw)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db.close()
    return {"message": "User registered successfully"}

@app.post("/login")
def login(user: UserLogin):
    db = SessionLocal()
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"message": "Login successful"}


@app.post("/process_log/")
async def process_log(entry: LogEntry):
    try:
        result = graph.invoke({"Log_entry": entry.log})
        label = result.get("label", "").lower()
        # if label == "critical":
        db_log = LOG_ENTRIES(Log=entry.log, Label=label)
        db = SessionLocal()
        db.add(db_log)
        db.commit()
        db.close()
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


