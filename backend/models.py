from sqlalchemy import Column, Integer, BigInteger, String, DateTime
from datetime import datetime
from database import Base

class FormData(Base):
    __tablename__ = "formdata"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    address = Column(String, index=True, nullable=True)
    contact = Column(BigInteger, index=True, nullable=True)
    email = Column(String, index=True, nullable=True)
    category = Column(String, default="General", index=True, nullable=True)
    notes = Column(String, nullable=True)
    image = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)


