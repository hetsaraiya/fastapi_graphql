from sqlalchemy import Column, String, Integer, ForeignKey, Double
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

    accounts = relationship("Account", back_populates="user")

class Bank(Base):
    __tablename__ = "bank"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    interest_rates = Column(Double)

    accounts = relationship("Account", back_populates="bank")

class Account(Base):
    __tablename__ = "account"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id")) 
    bank_id = Column(Integer, ForeignKey("bank.id")) 
    amount = Column(Integer)
    acc_type = Column(String)

    user = relationship("User", back_populates="accounts") 
    bank = relationship("Bank", back_populates="accounts")