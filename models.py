from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    login = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)

    tasks = relationship(
        "Task",
        back_populates="employee"
    )


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    date = Column(String, nullable=False)
    location = Column(String, nullable=False)
    employee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, nullable=False, default="NEW")
    worked_hours = Column(Float, nullable=False, default=0.0)
    photo_path = Column(String, nullable=True)

    employee = relationship(
        "User",
        back_populates="tasks"
    )