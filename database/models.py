from sqlalchemy import Column, Integer, String, BigInteger, Date, DateTime, Boolean
from database.base import Base
from datetime import datetime


class Servers(Base):
    __tablename__ = "servers"

    discord_server_id = Column(String, primary_key=True, nullable=False, autoincrement=False)
    discord_server_name = Column(String, nullable=False)
    timezone = Column(String, nullable=False)
 
    mention_role = Column(String, nullable=False)
    owner_role = Column(String, nullable=False)
    
    channel_id_schedule = Column(String, nullable=False)
    channel_id_reminder = Column(String, nullable=False)
    message_id_schedule = Column(String, nullable=False)

    teamup_calendarkey = Column(String, nullable=True)
    teamup_subcalendar_id = Column(String, nullable=True)


    def __init__(self, discord_server_id, discord_server_name, timezone, owner_role, mention_role, channel_id_schedule, channel_id_reminder, message_id_schedule):        
        self.discord_server_id = discord_server_id
        self.discord_server_name = discord_server_name
        self.timezone = timezone
        self.owner_role = owner_role
        self.mention_role = mention_role
        self.channel_id_reminder = channel_id_reminder
        self.channel_id_schedule = channel_id_schedule
        self.message_id_schedule = message_id_schedule

    def as_dict(self):
        return {
            "discord_server_id": self.discord_server_id,
            "discord_server_name": self.discord_server_name,
            "timezone": self.timezone,
            "mention_role": self.mention_role,
            "owner_role": self.owner_role,
            "channel_id_schedule": self.channel_id_schedule,
            "channel_id_reminder": self.channel_id_reminder,
            "message_id_schedule": self.message_id_schedule,
            "teamup_calendarkey": self.teamup_calendarkey,
            "teamup_subcalendar_id": self.teamup_subcalendar_id
        }

class Scrims(Base):
    __tablename__ = "scrims"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    discord_server_id = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    time_start = Column(DateTime, nullable=False)
    time_end = Column(DateTime, nullable=False)
    enemy_team = Column(String, nullable=False)
    teamup_event_id = Column(String, nullable=True)
    teamup_event_version = Column(String, nullable=True)

    notified = Column(Boolean)


    def __init__(self, discord_server_id, date, time_start, time_end, enemy_team):        
        self.discord_server_id = discord_server_id
        self.date = date
        self.time_start = time_start
        self.time_end = time_end
        self.enemy_team = enemy_team
        self.notified = False

    def as_dict(self):
        return {
            "id": self.id,
            "discord_server_id" : self.discord_server_id,
            "date": self.date,
            "time_start": self.time_start,
            "time_end": self.time_end,
            "enemy_team": self.enemy_team,
            "teamup_event_id": self.teamup_event_id,
            "teamup_event_version": self.teamup_event_version,
            "notified": self.notified
        }
