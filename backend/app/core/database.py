from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings

is_sqlite = settings.DATABASE_URL.startswith("sqlite")
is_postgres = settings.DATABASE_URL.startswith("postgresql")

# check_same_thread=False es requerido solo para SQLite
# sslmode=require es necesario para Neon (y cualquier PostgreSQL en la nube)
if is_sqlite:
    connect_args = {"check_same_thread": False}
elif is_postgres and "sslmode" not in settings.DATABASE_URL:
    connect_args = {"sslmode": "require"}
else:
    connect_args = {}


engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


# Dependencia reutilizable para los endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
