import requests
import config as cfg

def test_calendarkey(calendar_key):
    '''
        Tests calendar key by creating and deleting a sub-calendar
        Command: !teamup [calendar-key]
        vals    -   0           1
    '''
    # tries to create and delete sub-calendar
    cal_data = create_sub_calendar("Scrim bot test", 24, calendar_key)
    if "subcalendar" in cal_data:
        if delete_sub_calendar(cal_data["subcalendar"]["id"], calendar_key) == 204:
            return True
    else:
        return False


def create_sub_calendar(name, color, calendar_key):
    url = "https://api.teamup.com/%s/subcalendars" % calendar_key
    headers = {"Teamup-Token": cfg.teamup_apikey, 
               "Content-type": "application/json"}

    payload = {
	    "name": name, 
	    "active": "true", 
	    "color": color, 
	    "overlap": "true"
    }
    r = requests.post(url, headers=headers, json=payload)
    return r.json()

def delete_sub_calendar(id, calendar_key):
    url = "https://api.teamup.com/%s/subcalendars/%s" % (calendar_key, id)
    headers = {"Teamup-Token": cfg.teamup_apikey}

    r = requests.delete(url, headers=headers)
    return(r.status_code)

def create_event(start, end, title, calendar_key, subcalendar_id):
    url = "https://api.teamup.com/%s/events" % calendar_key
    headers = {"Teamup-Token": cfg.teamup_apikey, 
               "Content-type": "application/json"}

    payload = {
         "subcalendar_id": subcalendar_id,
        "start_dt": start,
        "end_dt": end,
        "all_day": "false",
        "rrule": "",
        "title": title,
        "who": "",
        "location": "",
        "notes": ""
    }

    r = requests.post(url, headers=headers, json=payload)
    return(r.json())