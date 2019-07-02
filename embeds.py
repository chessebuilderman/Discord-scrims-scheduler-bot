import discord
from datetime import datetime
from database.db import Database
from database.models import Scrims
from datetime import datetime, timedelta
from pytz import timezone, all_timezones

db = Database()

def add_embed_footer(embed):
    embed.set_footer(
        text="Scrims scheduler bot by BlueX | VPS time: " + datetime.now().strftime("%a, %d %b %Y %H:%M:%S"),
        icon_url="http://patrikpapso.com/images/avatar-128x128.png",
    )


def Info(title, description):
    embed = discord.Embed(title=":information_source: " + title, description=description, color=0x007BFF)
    add_embed_footer(embed)
    return embed


def Success(title, description):
    embed = discord.Embed(title=":white_check_mark: " + title, description=description, color=0x28A745)
    add_embed_footer(embed)
    return embed


def Error(title, description):
    embed = discord.Embed(title=":x: " + title, description=description, color=0xDC3545)
    add_embed_footer(embed)
    return embed


days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
def get_schedule_embed(start_date, end_date, server_id, server_timezone):
    
    fmt_date = "%Y-%m-%d"
    # server timezone
    server_tz = timezone(server_timezone)

    #print("No timezone given")
    #print(start_date)
    #print("Server timezone")
    #print(start_date.astimezone(server_tz))

    
    start_date_fmt = start_date.astimezone(server_tz).strftime(fmt_date)
    end_date_fmt = end_date.astimezone(server_tz).strftime(fmt_date)

    start_date = start_date.astimezone(server_tz)
    end_date = end_date.astimezone(server_tz)

    datetime_now_tz = datetime.now().astimezone(server_tz)

    # get all scrims from server between start_date and end_date
    with db.connect() as session:
        scrims_data = session.query(Scrims).filter(Scrims.discord_server_id == server_id).\
                                            filter(Scrims.date.between(start_date_fmt, end_date_fmt)).\
                                            order_by(Scrims.time_start).all()
        session.expunge_all()
    # create schedule embed 
    embed = discord.Embed(
        title="SCRIMS SCHEDULE {} - {}".format(start_date_fmt, end_date_fmt),
        color=0x007BFF,
    )
    embed.set_thumbnail(url="http://patrikpapso.com/images/schedule.png")
    add_embed_footer(embed)
    
    delta = end_date - start_date
    number_of_days = delta.days
    schedule = [[] for day in range(0, number_of_days + 1)]
    for scrim in scrims_data:
        # put scrims into array by their day in the week (easier to turn into day-name)
        sd = scrim.as_dict()
        if (sd["date"].timetuple().tm_yday -1) < (start_date.timetuple().tm_yday - 1):
            index = sd["date"].timetuple().tm_yday - 1 + 365 - (start_date.timetuple().tm_yday - 1)
        else:
            index = (sd["date"].timetuple().tm_yday - 1) - (start_date.timetuple().tm_yday - 1)
        schedule[index].append(sd)
    
    # timezone formating stuff
    utc_tz = timezone("UTC")
    fmt_date_scrim = "%d.%m.%Y"
    fmt = "%H:%M"
    i = 0
    for scrims_in_day in schedule:
        day_date = start_date + timedelta(days=i)
        if len(scrims_in_day) > 0:
            day_string = ""
            for scrim in scrims_in_day:
                utc_tz.localize(scrim["time_start"], is_dst=None)
                utc_tz.localize(scrim["time_end"], is_dst=None)

                time_start_server = scrim["time_start"].astimezone(server_tz)
                time_end_server = scrim["time_end"].astimezone(server_tz)
                if datetime_now_tz.date() > scrim["date"]:
                    day_string += "~~({}) {} - {} against {}~~\n".format(
                        id,
                        time_start_server.strftime(fmt),
                        time_end_server.strftime(fmt),
                        scrim["enemy_team"],
                    )
                else:
                    day_string += "`({}) {} - {} against {}`\n".format(
                        scrim["id"],
                        time_start_server.strftime(fmt),
                        time_end_server.strftime(fmt),
                        scrim["enemy_team"],
                    )
        else:
            day_string = "NO SCRIMS SCHEDULED"
        embed.add_field(
            name=":calendar: **{}** ({})".format(
                days[day_date.weekday()], day_date.strftime(fmt_date_scrim)
            ),
            value=day_string,
            inline=False,
        )
        i = i + 1

    embed.add_field(name="Timezone", value=server_timezone, inline=True)
    return embed