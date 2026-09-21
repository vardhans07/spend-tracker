from sqlalchemy import Column, Integer, Float, String, Date
from app.database import Base

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    category = Column(String, index=True, nullable=False)
    note = Column(String, default="")
    date = Column(Date, nullable=False)
