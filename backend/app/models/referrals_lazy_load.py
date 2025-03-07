from sqlalchemy import Column, Integer, ForeignKey, BigInteger, String
from app.database import BaseReferral
from sqlalchemy.orm import relationship

class ReferralsLazyLoad(BaseReferral):
    __tablename__ = 'referrals'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    telegram_id = Column(BigInteger, nullable=False)
    referral_link = Column(String, nullable=False)
    invited_count = Column(Integer, default=0)
    referrer_id = Column(BigInteger, ForeignKey('users.telegram_id'), nullable=True)
    referred_by = Column(Integer, ForeignKey('users.id'), nullable=True)

    user = relationship("UserLazyLoad", foreign_keys=[user_id], back_populates="referrals")
    referrer = relationship("UserLazyLoad", foreign_keys=[referrer_id], back_populates="referred_by")
