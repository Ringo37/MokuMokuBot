from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey


Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    discord_id = Column(String(18), unique=True)
    logs = relationship("VoiceLog", back_populates="user")


class VoiceLog(Base):
    __tablename__ = "voice_log"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    join_time = Column(DateTime)
    leave_time = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=True)

    user = relationship("User", back_populates="logs")
