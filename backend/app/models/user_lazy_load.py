from sqlalchemy import Column, Integer, BigInteger, String, Boolean, TIMESTAMP, func
from sqlalchemy.orm import relationship
from app.database import BaseReferral

class UserLazyLoad(BaseReferral):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True)  
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    language_code = Column(String(10))
    is_bot = Column(Boolean, default=False)
    photo_url = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    balance = relationship("Balance", back_populates="user", uselist=False)
    transactions = relationship("Transaction", back_populates="user")
    referrals = relationship("ReferralsLazyLoad", back_populates="user", foreign_keys="[ReferralsLazyLoad.user_id]")
    referred_by = relationship("ReferralsLazyLoad", back_populates="referrer", foreign_keys="[ReferralsLazyLoad.referrer_id]", uselist=False)