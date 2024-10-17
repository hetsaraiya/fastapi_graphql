from sqlalchemy import Column, String, Integer, ForeignKey, Double, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone = Column(Integer)
    profile_url = Column(String)
    email = Column(String)
    password = Column(String)
    address = Column(String)
    is_admin=Column(Boolean)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    is_deleted = Column(Boolean)

    accounts = relationship("Account", back_populates="user")

class Bank(Base):
    __tablename__ = "bank"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    interest_rates = Column(Double)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    is_deleted = Column(Boolean)

    accounts = relationship("Account", back_populates="bank")

class Account(Base):
    __tablename__ = "account"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id")) 
    bank_id = Column(Integer, ForeignKey("bank.id")) 
    amount = Column(Integer)
    acc_type = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    is_deleted = Column(Boolean)

    user = relationship("User", back_populates="accounts") 
    bank = relationship("Bank", back_populates="accounts")