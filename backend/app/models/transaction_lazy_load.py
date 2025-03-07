# app/models/transaction_lazy_load.py
from sqlalchemy import Column, Integer, Float, ForeignKey, String
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.user_lazy_load import UserLazyLoad  # Убедитесь, что это импортируется корректно

class TransactionLazyLoad(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String(50), nullable=False)  # deposit, withdraw, transfer_to_trade, profit, loss

    user = relationship("UserLazyLoad", back_populates="transactions")  # Связь с UserLazyLoad
