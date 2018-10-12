from sqlalchemy import Column, Integer, String, BigInteger, Date
from database.base import Base
from datetime import datetime


class Servers(Base):
    __tablename__ = "servers"

    discord_server_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=False)
    discord_server_name = Column(String)
    timezone = Column(String)
 
    mention_role = Column(BigInteger)
    owner_role = Column(BigInteger, nullable=False)
    
    channel_id_schedule = Column(BigInteger)
    channel_id_reminder = Column(BigInteger)
    message_id_schedule = Column(BigInteger)


    def __init__(self, owner_role, discord_server_id, discord_server_name):
        self.owner_role = owner_role
        self.discord_server_id = discord_server_id
        self.discord_server_name = discord_server_name

    def as_dict(self):
        return {
            "discord_server_id": self.discord_server_id,
            "discord_server_name": self.discord_server_name,
            "timezone": self.timezone,
            "mention_role": self.mention_role,
            "owner_role": self.owner_role,
            "channel_id_schedule": self.channel_id_schedule,
            "channel_id_reminder": self.channel_id_reminder,
            "message_id_schedule": self.message_id_schedule
        }
