import discord
from datetime import datetime
from database.db import Database
from database.models import Scrims
from datetime import datetime, timedelta
from pytz import timezone, all_timezones

db = Database()

def add_embed_footer(embed):
    embed.set_footer(
        text="Scrims scheduler bot by BlueX | " + datetime.now().strftime("%a, %d %b %Y %H:%M:%S"),
        icon_url="https://cdn.discordapp.com/avatars/162554458469957632/c84e8dc5798eb16113f915c4443b15ab.png",
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
    start_date_fmt = start_date.strftime(fmt_date)
    end_date_fmt = end_date.strftime(fmt_date)
    # get all scrims from server between start_date and end_date
    with db.connect() as session:
        scrims_data = session.query(Scrims).filter(Scrims.discord_server_id == server_id).\
                                            filter(Scrims.date.between(start_date_fmt, end_date_fmt)).all()
        session.expunge_all()
    # create schedule embed 
    embed = discord.Embed(
        title="SCRIMS SCHEDULE {} - {}".format(start_date_fmt, end_date_fmt),
        color=0x007BFF,
    )
    embed.set_thumbnail(url="http://icons-for-free.com/free-icons/png/512/497220.png")
    add_embed_footer(embed)
    
    delta = end_date - start_date
    number_of_days = delta.days
    schedule = [[] for day in range(0, number_of_days + 1)]
    for scrim in scrims_data:
        # put scrims into array by their day in the week (easier to turn into day-name)
        sd = scrim.as_dict()
        index = (sd["date"].timetuple().tm_yday - 1) - (start_date.timetuple().tm_yday - 1)
        schedule[index].append(sd)
    
    # timezone formating stuff
    server_tz = timezone(server_timezone)
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
                if datetime.today().date() > scrim["date"]:
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