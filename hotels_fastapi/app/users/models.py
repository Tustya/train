from sqlalchemy import JSON, BigInteger, Column, Computed, Date, ForeignKey, Integer, String
from hotels_fastapi.app.database import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(512), nullable=False)
    hashed_password = Column(String(1024), nullable=False)