import discord
from singletons.disc import Discord_bot
import random
from datetime import datetime, timedelta
import time
import math
import dateutil.parser
from pytz import timezone, all_timezones
from database.models import Servers, Scrims
from database.db import Database
import embeds
import teamup
import re


disc = Discord_bot()
client = disc.get_client()

db = Database()

class Scrim_bot:
    commands = []

    async def setup(self, message):
        '''
		    Command: !setup [timezone] [owner] [mention] [schedule-channel] [reminder-channel]
              vals -    0       1
            Whole setup is contained in one command to keep it simple
        '''
        vals = message.content.split(" ")
        if vals[1] in all_timezones:
            # Check if 2 roles were mentioned 0 - owner, 1 - reminders
            role_mentions = re.findall(r'<@&(\d{17,19})>', message.content)
            channel_mentions = re.findall(r'<#(\d{17,19})>', message.content)
            if len(role_mentions) >= 1:
                owner_role_id = role_mentions[0]
                reminder_role_id = role_mentions[1] if len(role_mentions) >= 2 else role_mentions[0]
                # Check if 2 channels were mentioned 0 - schedule, 1 - reminders
                if len(channel_mentions) == 2:
                    schedule_channel_id = channel_mentions[0]
                    reminder_channel_id = channel_mentions[1]
                    msg = await disc.send_message(discord.Object(schedule_channel_id), "...")
                    if msg is not None:
                        # Save server data to server for future use
                        with db.connect() as session:
                            res = session.query(Servers).filter(Servers.discord_server_id == message.server.id).count()
                            session.expunge_all()
                        if res == 0:
                            with db.connect() as session:
                                server = Servers(message.server.id, message.server.name, vals[1], owner_role_id, reminder_role_id, schedule_channel_id, reminder_channel_id, msg.id)
                                session.add(server)
                            print("new server - " + message.server.name)
                        else:
                            with db.connect() as session:
                                update_res = session.query(Servers).filter(Servers.discord_server_id == message.server.id).\
                                                                    update({"owner_role": owner_role_id,
                                                                            "mention_role": reminder_role_id,
                                                                            "channel_id_schedule": schedule_channel_id,
                                                                            "channel_id_reminder": reminder_channel_id,
                                                                            "message_id_schedule": msg.id,
                                                                            "timezone": vals[1]})
                        
                                session.expunge_all()
                        await self.update_schedule(message)
                        # get saved channel names
                        schedule_channel_name = message.server.get_channel(schedule_channel_id)
                        reminder_channel_name = message.server.get_channel(reminder_channel_id)
                        # since discordpy doesnt give me role by id, I will pull out the role from message itself by id
                        owner_role_name = ""
                        reminder_role_name = ""
                        for role in message.role_mentions:
                            if role.id == owner_role_id:
                                owner_role_name = role.name
                            if role.id == reminder_role_id:
                                reminder_role_name = role.name
                        await disc.send_message(message.channel, embed=embeds.Success("Server has been setup", "You have successfuly set up the server\nOwner: %s\nMention: %s\nSchedule: %s\nReminder: %s" % (owner_role_name, reminder_role_name, schedule_channel_name, reminder_channel_name)))
                    else:
                        await disc.send_message(message.channel, embed=embeds.Error("Error sending a schedule message", "Make sure the bot has permissions to write into channel you specified for schedule."))
                else:
                    await disc.send_message(message.channel, embed=embeds.Error("Wrong arguments", "You need to provide 2 channel (schedule + reminders)"))
            else:
                await disc.send_message(message.channel, embed=embeds.Error("Wrong arguments", "You need to provide 2 mentionable roles (owner + reminder)"))
        else:
            await disc.send_message(message.channel, embed=embeds.Error("Wrong arguments", "Unknown timezone, try to use this [LINK](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) for reference."))
   
    async def add_scrim(self, message):
        '''
           Command: !scrimadd [dd/mm] [hh:mm] [hh:mm] [enemy-team-name]
              vals -    0         1       2       3            4
           Creates a new scrim entry, replies with embed containing information about added scrim
        '''
        vals = message.content.split(" ")
        if len(vals) >= 5:
            with db.connect() as session:
                query = (
                    session.query(Servers)
                    .filter_by(discord_server_id=message.server.id)
                    .first()
                )
                session.expunge_all()

            server_data = query.as_dict()
            # parse date
            dt_now = datetime.now()
            date = vals[1].split("/")
            # this format has to be mm/dd/yyyy
            scrim_date = "{}/{}/{}".format(date[1], date[0], dt_now.year)
                # TODO: Implement ability to add scrims for next year
                # Just check for date being in the past, if it's in the past, it's happening next year
            # datetime formatting
            fmt = "%H:%M"
            fmt_date = "%Y-%m-%d"
            server_tz = timezone(server_data["timezone"]) 
            utc_tz = timezone("UTC")
            # ugly time formatting practice
            ts = vals[2].split(":") # time-start
            te = vals[3].split(":") # time-end
            # localize this datetime to server's timezone
            time_start_tz = server_tz.localize(datetime(dt_now.year, int(date[1]), int(date[0]), int(ts[0]), int(ts[1]), 0))
            time_end_tz   = server_tz.localize(datetime(dt_now.year, int(date[1]), int(date[0]), int(te[0]), int(te[1]), 0))
            # localize these datetimes to UTC for database storage
            utc_ts = time_start_tz.astimezone(utc_tz)
            utc_te = time_end_tz.astimezone(utc_tz)
            # parse enemy-team-name
            enemy_team_name = " ".join(str(x) for x in vals[4:])
            # save the entry into database
            with db.connect() as session:
                scrim = Scrims(message.server.id, scrim_date, utc_ts, utc_te, enemy_team_name)
                session.add(scrim)
                session.flush()
                session.expunge_all()

            # get added data
            scrim = scrim.as_dict()
            # embed to inform user about successful add
            embed = embeds.Success("Scrim added", "Scrim has been successfully added")
            embed.add_field(name="Scrim ID", value=scrim["id"], inline=True)
            embed.add_field(name="Date", value=time_start_tz.strftime(fmt_date), inline=False)
            embed.add_field(name="Timezone", value=time_end_tz.tzinfo, inline=True)
            embed.add_field(name="Start of the scrim", value=time_start_tz.strftime(fmt), inline=True)
            embed.add_field(name="End of the scrim", value=time_end_tz.strftime(fmt), inline=True)
            embed.add_field(name="Opponent", value=enemy_team_name, inline=False)

            # send embed as a response
            await disc.send_message(message.channel, embed=embed)
            # update schedule with current changes
            await self.update_schedule(message)

            # Teamup add
            if server_data["teamup_calendarkey"] is not None and server_data["teamup_subcalendar_id"] is not None:
                iso_fmt = "%Y-%m-%dT%H:%M%SZ" #2015-01-31T10:00:00Z
                tup_data = teamup.create_event(utc_ts.strftime(iso_fmt), utc_te.strftime(iso_fmt), "Scrim vs %s" % enemy_team_name, server_data["teamup_calendarkey"], server_data["teamup_subcalendar_id"])
                if "error" in tup_data:
                    await disc.send_message(message.channel, embed=embeds.Error("TeamUP Error", tup_data["error"]["message"]))    
                else:
                    with db.connect() as session:
                        res = session.query(Scrims).filter(Scrims.id == scrim["id"]).\
                                                    update({"teamup_event_id": tup_data["event"]["id"],
                                                            "teamup_event_version": tup_data["event"]["version"]})
                        session.expunge_all()

                    if res == 1:
                        await disc.send_message(message.channel, embed=embeds.Success("Added to TeamUP", "Scrim has been successfuly added to TeamUP calendar"))
        else:
            await disc.send_message(message.channel, embed=embeds.Error("Wrong arguments", "Wrong argument provided, use `!scrimadd help` for help"))          
            return

    async def delete_scrim(self, message):
        '''
            Deletes scrims by ID
            Command: !scrimdelete [ID]
            vals -      0           1
        '''
        vals = message.content.split(" ")
        if len(vals) == 2:
            with db.connect() as session:
                server = session.query(Servers).filter_by(discord_server_id=message.server.id).first()
                scrim = session.query(Scrims).filter(Scrims.id == vals[1]).first()
                res = session.query(Scrims).filter(Scrims.id == vals[1]).filter(Scrims.discord_server_id == message.server.id).delete()
                session.expunge_all()
            
            if res == 1:
                await disc.send_message(message.channel, embed=embeds.Success("Succesfully deleted scrim", "Scrim with ID %s has been deleted" % vals[1]))
                # update schedule with current changes
                await self.update_schedule(message)

                # if TeamUP is connected, delete from there as well
                scrim = scrim.as_dict()
                server = server.as_dict()
                if server["teamup_calendarkey"] is not None:
                    status_code = teamup.delete_event(server["teamup_calendarkey"], scrim["teamup_event_id"], scrim["teamup_event_version"])
                    if status_code == 200:
                        await disc.send_message(message.channel, embed=embeds.Success("Deleted from TeamUP", "Scrim has been successfuly deleted from TeamUP calendar"))
                    else:
                        await disc.send_message(message.channel, embed=embeds.Error("Error deleting from TeamUP", "Error occured while deleting from TeamUP calendar, event doesn't exist or it has be edited (delete manually)"))
            else:
                await disc.send_message(message.channel, embed=embeds.Error("Wrong arguments", "No scrim has been deleted, either ID doesn't exist or this scrim doesn't belong to this server."))          
        else:
            await disc.send_message(message.channel, embed=embeds.Error("Wrong arguments", "Wrong argument provided, use `!scrimdelete help` for help"))

    async def edit_scrim(self, message):
        '''
            Edits already existing scrim by ID
            Command: !scrimedit [ID] [new dd/mm] [new hh:mm] [new hh:mm] [new enemy-team]
            vals -      0         1     2           3             4             5
        '''
        vals = message.content.split(" ")
        if len(vals) >= 6:
            # identical parsing to !scrimadd, just shifted arguments (cuz of ID)
            with db.connect() as session:
                query = session.query(Servers).filter_by(discord_server_id=message.server.id).first()
                session.expunge_all()

            server_data = query.as_dict()
            # parse date
            dt_now = datetime.now()
            date = vals[2].split("/")
            # this format has to be mm/dd/yyyy
            scrim_date = "{}/{}/{}".format(date[1], date[0], dt_now.year)
                # TODO: Implement ability to add scrims for next year
                # Just check for date being in the past, if it's in the past, it's happening next year
            # datetime formatting
            fmt = "%H:%M"
            fmt_date = "%Y-%m-%d"
            server_tz = timezone(server_data["timezone"]) 
            utc_tz = timezone("UTC")
            # ugly time formatting practice
            ts = vals[3].split(":") # time-start
            te = vals[4].split(":") # time-end
            # localize this datetime to server's timezone
            time_start_tz = server_tz.localize(datetime(dt_now.year, int(date[1]), int(date[0]), int(ts[0]), int(ts[1]), 0))
            time_end_tz   = server_tz.localize(datetime(dt_now.year, int(date[1]), int(date[0]), int(te[0]), int(te[1]), 0))
            # localize these datetimes to UTC for database storage
            utc_ts = time_start_tz.astimezone(utc_tz)
            utc_te = time_end_tz.astimezone(utc_tz)
            # parse enemy-team-name
            enemy_team_name = " ".join(str(x) for x in vals[5:])
            
            # update record in database
            with db.connect() as session:
                server = session.query(Servers).filter_by(discord_server_id=message.server.id).first()
                # I only need teamup_event_id and teamup_event_version, so it's fine querying it before edit
                scrim = session.query(Scrims).filter(Scrims.id == vals[1]).first() 
                res = session.query(Scrims).filter(Scrims.discord_server_id == message.server.id).\
                                            filter(Scrims.id == vals[1]).\
                                            update({"date": scrim_date,
                                                    "time_start": utc_ts,
                                                    "time_end": utc_te,
                                                    "enemy_team": enemy_team_name})
                session.expunge_all()
            
            if res == 1:
                # embed to inform user about successful edit
                embed = embeds.Success("Scrim edited", "Scrim has been successfully edited")
                embed.add_field(name="Date", value=time_start_tz.strftime(fmt_date), inline=False)
                embed.add_field(name="Timezone", value=time_end_tz.tzinfo, inline=True)
                embed.add_field(name="Start of the scrim", value=time_start_tz.strftime(fmt), inline=True)
                embed.add_field(name="End of the scrim", value=time_end_tz.strftime(fmt), inline=True)
                embed.add_field(name="Opponent", value=enemy_team_name, inline=False)
                await disc.send_message(message.channel, embed=embed)
                # update schedule with current changes
                await self.update_schedule(message)

                # If TeamUP is connected, edit there as well
                scrim = scrim.as_dict()
                server = server.as_dict()
                if server["teamup_calendarkey"] is not None:
                    iso_fmt = "%Y-%m-%dT%H:%M%SZ" #2015-01-31T10:00:00Z
                    tup_data = teamup.edit_event(server["teamup_calendarkey"],
                                                  server["teamup_subcalendar_id"],
                                                  scrim["teamup_event_id"],
                                                  scrim["teamup_event_version"],
                                                  utc_ts.strftime(iso_fmt),
                                                  utc_te.strftime(iso_fmt),
                                                  "Scrim vs %s" % enemy_team_name)
                    if "error" in tup_data:
                        await disc.send_message(message.channel, embed=embeds.Error("TeamUP Error", tup_data["error"]["message"]))
                    else:
                        with db.connect() as session:
                            res = session.query(Scrims).filter(Scrims.discord_server_id == message.server.id).\
                                                        filter(Scrims.id == vals[1]).\
                                                        update({"teamup_event_version": tup_data["event"]["version"]})
                            session.expunge_all()
                        if res == 1:
                            await disc.send_message(message.channel, embed=embeds.Success("Edited in TeamUP", "Scrim has been successfuly edited in TeamUP calendar"))
            else:
                await disc.send_message(message.channel, embed=embeds.Error("Wrong arguments", "No scrim has been edited, either ID doesn't exist or this scrim doesn't belong to this server."))          
        else:
            await disc.send_message(message.channel, embed=embeds.Error("Wrong arguments", "Wrong argument provided, use `!scrimedit help` for help"))

    #
    # TODO - in one function plzzzzzzzz
    #
    async def update_schedule(self, message):
        today = datetime.today()
        week_from_today = today + timedelta(days=7)

        with db.connect() as session:
            query = session.query(Servers).filter(Servers.discord_server_id == message.server.id).first()
            session.expunge_all()
        
        if query is not None:
            server_data = query.as_dict()
            schedule_embed = embeds.get_schedule_embed(today, week_from_today, server_data["discord_server_id"], server_data["timezone"])
            msg = await disc.get_message(discord.Object(server_data["channel_id_schedule"]), server_data["message_id_schedule"])
            if msg is not None:
                await disc.edit_message(msg, embed=schedule_embed)
            else:
                await disc.send_message(message.channel, embed=embeds.Error("Schedule message not found", "Schedule update unsuccessful, you probably deleted schedule message, setup server again to create a new one."))          

    async def update_schedule_by_server_id(self, server_id):
        today = datetime.today()
        week_from_today = today + timedelta(days=7)

        with db.connect() as session:
            query = session.query(Servers).filter(Servers.discord_server_id == server_id).first()
            session.expunge_all()
        
        if query is not None:
            server_data = query.as_dict()
            schedule_embed = embeds.get_schedule_embed(today, week_from_today, server_data["discord_server_id"], server_data["timezone"])
            msg = await disc.get_message(discord.Object(server_data["channel_id_schedule"]), server_data["message_id_schedule"])
            if msg is not None:
                await disc.edit_message(msg, embed=schedule_embed)

    #---------------------------------------------------------------------------------------
    # TEAM UP STUFF
    #--------------------------------------------------------------------------------------- 
    async def teamup_setup(self, message):
        '''
            Tests calendar key by creating and deleting a sub-calendar
            Command: !teamup [calendar-key]
            vals    -   0           1
        '''
        vals = message.content.split(" ")
        if len(vals) == 2:
            if vals[1] == "-":
                 with db.connect() as session:
                    res = session.query(Servers).filter(Servers.discord_server_id == message.server.id).\
                                                 update({"teamup_calendarkey": None,
                                                         "teamup_subcalendar_id": None})
                    session.expunge_all()
                 if res == 1:
                     await disc.send_message(message.channel, embed=embeds.Success("TeamUP API disconnected", "TeamUP has been succesfuly disconnected"))
            # test calendar key
            data = teamup.create_sub_calendar("Scrim bot subcalendar", 18, vals[1])
            if data is not None:
                # save this key to database
                if data is not None:
                    with db.connect() as session:
                        res = session.query(Servers).filter(Servers.discord_server_id == message.server.id).\
                                                     update({"teamup_calendarkey": vals[1],
                                                             "teamup_subcalendar_id": data["subcalendar"]["id"]})
                        session.expunge_all()
                
                    await disc.send_message(message.channel, embed=embeds.Success("TeamUP API connected", "New sub-calendar has been created on your TeamUP calendar"))
            else:
                await disc.send_message(message.channel, embed=embeds.Error("Something went wrong with TeamUP", "Calendarkey is invalid or request took too long, try again later..."))
        else:
            await disc.send_message(message.channel, embed=embeds.Error("Wrong arguments", "Wrong argument provided, use `!teamup help` for help"))
    
    async def teamup_changed(self, server_id):
        '''
            ---
        '''
        with db.connect() as session:
            query = session.query(Servers).filter(Servers.discord_server_id == server_id).first()
            session.expunge_all()

        if query is not None:
            server_data = query.as_dict()
            fmt_date = "%Y-%m-%d"
            dt_now = datetime.now()
            dt_now_m = dt_now - timedelta(days=1) # cuz between is weird and left bound is < and not <=
            dt_week_later = dt_now + timedelta(days=7)
            
            tudata = teamup.get_events_between_dates(server_data["teamup_calendarkey"], dt_now.strftime(fmt_date), dt_week_later.strftime(fmt_date), server_data["teamup_subcalendar_id"])
            if "error" not in tudata:
                # Get scrims for current week from database
                with db.connect() as session:
                    scrims_query = session.query(Scrims).filter(Scrims.discord_server_id == server_id).\
                                                   filter(Scrims.date.between(dt_now_m, dt_week_later)).all()
                    session.expunge_all()

                if scrims_query is not None:
                    scrims_event_ids = []
                    for scrim in scrims_query:
                        sd = scrim.as_dict()
                        scrims_event_ids.append(sd["teamup_event_id"]) # save events from db, so we can check later newly added
                        found = False # later to check that it was deleted
                        for event in tudata["events"]: 
                            if event["id"] == sd["teamup_event_id"]:
                                found = True
                                if event["version"] != sd["teamup_event_version"]:
                                    # the event has been edited on teamup
                                    utc_tz = timezone("UTC")
                                    fmt_date = "%Y-%m-%d"
                                    # date parsing
                                    start = dateutil.parser.parse(event["start_dt"])
                                    end = dateutil.parser.parse(event["end_dt"])
                                    # put time_start/time_end into utc timezone
                                    utc_ts = start.astimezone(utc_tz)
                                    utc_te = end.astimezone(utc_tz)
                                    # pull date of the scrim from time_start
                                    scrim_date = utc_ts.strftime(fmt_date)
                                    # enemy team name from event's title
                                    new_title = event["title"]
                                    # save the entry into database
                                    with db.connect() as session:
                                        res = session.query(Scrims).filter(Scrims.discord_server_id == server_id).\
                                                                    filter(Scrims.teamup_event_id == event["id"]).\
                                                                    update({"date": scrim_date,
                                                                            "time_start": utc_ts,
                                                                            "time_end": utc_te,
                                                                            "enemy_team": new_title,
                                                                            "teamup_event_version": event["version"]})
                        # check for deleted scrim
                        if not found:
                            # this scrim is not on teamup, delete it
                            with db.connect() as session:
                                res = session.query(Scrims).filter(Scrims.discord_server_id == server_id).\
                                                            filter(Scrims.id == sd["id"]).\
                                                            delete()
                    # check for newly added scrims
                    for event in tudata["events"]:
                        if event["id"] not in scrims_event_ids:
                            utc_tz = timezone("UTC")
                            fmt_date = "%Y-%m-%d"
                            # date parsing
                            start = dateutil.parser.parse(event["start_dt"])
                            end = dateutil.parser.parse(event["end_dt"])
                            # put time_start/time_end into utc timezone
                            utc_ts = start.astimezone(utc_tz)
                            utc_te = end.astimezone(utc_tz)
                            # pull date of the scrim from time_start
                            scrim_date = utc_ts.strftime(fmt_date)
                            # enemy team name from event's title
                            enemy_team_name = event["title"]
                            # save the entry into database
                            with db.connect() as session:
                                scrim = Scrims(server_id, scrim_date, utc_ts, utc_te, enemy_team_name, event["id"], event["version"])
                                session.add(scrim)
                                session.flush()
                                session.expunge_all()