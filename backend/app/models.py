from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, index=True)  # timestamptz
    message = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False, index=True)  # INFO, WARNING, ERROR, CRITICAL
    source = Column(String(100), nullable=False, index=True)

    def __repr__(self):
        return f"<Log(id={self.id}, severity={self.severity}, source={self.source})>"
