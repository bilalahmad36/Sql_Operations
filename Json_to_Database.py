from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json

server = 'DESKTOP-G5V0UP1\\SQLEXPRESS'
database = 'Log_File'
driver = 'ODBC+Driver+18+for+SQL+Server'

DATABASE_URL = f'mssql+pyodbc://@{server}/{database}?driver={driver}&trusted_connection=yes&Encrypt=no'

engine = create_engine(DATABASE_URL)
Sessionlocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)
Base = declarative_base()

# --- ORM Model (TABLE)---
class Employees(Base):
    __tablename__ = "employees_data"
    id = Column(Integer, primary_key=True, index=True)
    Name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)


Base.metadata.create_all(bind=engine)


file = open("employees.json", "r")
data = json.load(file)
print(type(data))


db = Sessionlocal()
for emp in data["employees"]:
    db_user = Employees(Name=emp["firstName"], last_name=emp["lastName"])
    db.add(db_user)


db.commit()
db.close()    

print("✅ All employee records inserted successfully!")