from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import pyodbc
from dotenv import load_dotenv

load_dotenv(override=True)

print("✅ DATABASE_URL cargada correctamente")

def get_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=.\\SQLEXPRESS;"
        "DATABASE=SmartParking;"
        "UID=sa;"
        "PWD=jhomy1403;"
        "Encrypt=no;"
        "TrustServerCertificate=yes;"
    )

engine = create_engine(
    "mssql+pyodbc://",
    creator=get_connection,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()