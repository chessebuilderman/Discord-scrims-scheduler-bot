# Discord scrim bot
This project is a simple solution for teams to schedule their [scrims](https://www.urbandictionary.com/define.php?term=scrim) on Discord that includes Reminders (15 minutes before the scrim) and usage of [TeamUP](https://www.teamup.com/) API to use this service as a free Web Interface for cool looking calendar.

I'm currently hosting this bot on my private VPS with Postgres database handling all the data. 

If you wish to support the maintenance and caffeine costs -> 

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.me/bluexow)

## How to use the bot
1. Add the bot to your server via this [link](https://discordapp.com/api/oauth2/authorize?client_id=494030719715377152&permissions=0&scope=bot)
2. Give the bot permissions to write/read channels you wish to use as schedule/reminders/commands etc.
3. Setup the bot with command `!setup [timezone] [owner-role] [mention-role] [schedule-channel] [mention-channel]`
4. If you wish to use TeamUP as a Web Interface, provide the *calendarkey* with `!teamup [calendarkey]`
5. Now you are ready to add/edit/delete scrims with commands `!scrimadd` `!scrimedit` `!scrimdelete`, If you need a help with any of the commands, use `![command] help` (`!scrimadd help`, `!setup help`, `!teamup help` etc.)

**Notes:**
- Available timezones can be found [here](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)
- When setting up the bot, **mention** the roles/channels in the message (@manager, #schedule etc.)
- **TeamUP**: Create your free acount [here](https://www.teamup.com/), create new calendar and provide the bot with **ADMIN** permissions `calendarkey` (Example: ks73ad7816e7a61b3a - `!teamup ks73ad7816e7a61b3a`), to disconnect the TeamUP use command `!teamup -`

## How to run the bot yourself
Python version: `3.6`
Postgres version: `10.5-1`
Used libraries: 
```python
pip install discord.py
pip install pytz
pip install psycopg2
pip install SQLAlchemy
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
