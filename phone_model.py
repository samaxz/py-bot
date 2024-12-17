from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Phone(Base):
  __tablename__ = 'phones'

  id = Column(Integer, primary_key=True, index=True)
  phone = Column(String, unique=True, index=True)
