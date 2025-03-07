# app/models/balance_lazy_load.py
from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.user_lazy_load import UserLazyLoad  # Убедитесь, что это импортируется корректно

class BalanceLazyLoad(Base):
    __tablename__ = 'balances'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    balance = Column(Float, default=0.0)  # Основной баланс
    trade_balance = Column(Float, default=0.0)  # Торговый баланс
    frozen_balance = Column(Float, default=0.0)  # Замороженные средства
    earned_balance = Column(Float, default=0.0)  # Чистая прибыль

    user = relationship(UserLazyLoad, back_populates="balance")  # Связь с UserLazyLoad
