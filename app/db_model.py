from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100))
    last_name = Column(String(255))
    role = Column(String(20))  # TODO: create enum for instructor/student/admin
    email = Column(String(100), unique=True)
    password = Column(String)


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), unique=True)
    description = Column(String(1000))
    duration = Column(Integer)
