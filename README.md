# Discord scrim bot
> In case of any problems/bugs/need of friends, join the community discord [HERE](scheduler.patrikpapso.com)

This project is a simple solution for teams to schedule their [scrims](https://www.urbandictionary.com/define.php?term=scrim) on Discord that includes reminders (15 minutes before the scrim) and usage of [TeamUP](https://www.teamup.com/) API to use this service as a free Web Interface for cool looking calendar.


I'm currently hosting this bot on my private VPS with Postgres database handling all the data. 

If you wish to support the maintenance and caffeine costs -> 

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.me/bluexow)

## Features
**Screenshots are all the way at the bottom, so they don't take too much space**
- Having a scrim schedule directly in Discord
- Reminders about scrims for those that always forget
- Ability to use TeamUP as a cool web-interface for the calendar
- Automatic synchronization with TeamUP
- Available commands - for more information about these commands type command + help (e.g. `!scrimadd help`)
    - `!setup`
    - `!scrimadd`
    - `!scrimedit`
    - `!scrimdelete`
    - `!teamup`
    - `!update`

## How to setup the bot
1. Add the bot to your server via this [https://discordapp.com/api/oauth2/authorize?client_id=494030719715377152&permissions=0&scope=bot](https://discordapp.com/api/oauth2/authorize?client_id=494030719715377152&permissions=0&scope=bot)
2. Give the bot permissions to write/read channels you wish to use as schedule/reminders/commands etc.
3. Setup the bot with command `!setup [timezone] [owner-role] [mention-role] [schedule-channel] [reminder-channel]`
    - Example: `!setup Europe/Bratislava @manager @member #schedule #reminder` - timezones can be found [here](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones), always include whole string from column `TZ*` (in this case Europe/Bratislava)
4. If you wish to use TeamUP as a Web Interface, provide the *calendarkey* with `!teamup [calendarkey]`
    - ![calendarkey](http://bot.patrikpapso.com/teamup_calendarkey.png)
5. Now you are ready to add/edit/delete scrims with commands `!scrimadd` `!scrimedit` `!scrimdelete`, If you need a help with any of the commands, use `![command] help` (`!scrimadd help`, `!setup help`, `!teamup help` etc.)
    - Example of add a scrim: `!scrimadd 24/10 18:00 20:00 Dallas Fuel` - adding a scrim on 24th of October, from 18:00 to 20:00 (in chosen timezone) against Dallas Fuel
    - Example of edit a scrim: `!scrimedit 1 25/10 20:00 22:00 Florida Mayhem` - editing a scrim with ID 1 with new data
    - Example of delete a scrim: `!scrimdelete 1` - deleting a scrim with ID 1

**Notes:**
- When setting up the bot, **mention** the roles/channels in the message (@manager, #schedule etc.)
- **TeamUP**: Create your free acount [here](https://www.teamup.com/), create new calendar and provide the bot with **ADMIN** permissions `calendarkey` (Example: ks73ad7816e7a61b3a - `!teamup ks73ad7816e7a61b3a`), to disconnect the TeamUP use command `!teamup -`

## How to run the bot yourself
- Not needed if you just want to use the bot

Python version: `3.6`
Postgres version: `10.5-1`
Used libraries: 
```python
pip install discord.py
pip install pytz
pip install psycopg2
pip install SQLAlchemy
pip install python-dateutil==2.6.0
```
To run the bot yourself, you need to create `config.py` that includes:
```python
postgres = {
    "host": "host",
    "database": "database",
    "user": "user",
    "password": "password"
    }
bot = {
    "version" : "dev", # dev/prod - defines used token below
    "dev_token": "login_token",
    "prod_token": "login_token"
    }
teamup_apikey = ""
```
Discord bot token can be obtained [here](https://discordapp.com/developers/applications/)
TeamUP API token can be obtained [here](https://teamup.com/api-keys/request)

I'm not a big-boy Python programmer, so if you wish to refactor the code and teach me something, feel free to do so!

## Screenshots showcase
>Adding a scrim

![Scrim-add](http://bot.patrikpapso.com/scrim-add.png)

>Static schedule of the current week:

![Static-schedule](http://bot.patrikpapso.com/static-schedule.png)

>Reminder about scrim ~15 minutes before scrim:

![Scrim-reminder](http://bot.patrikpapso.com/reminder.png)

>TeamUP Calendar:

![Teamup-calendar](http://bot.patrikpapso.com/teamup-calendar.png)
