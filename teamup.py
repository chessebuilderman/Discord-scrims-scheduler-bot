import requests
import config as cfg

def test_calendarkey(calendar_key):
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
    if r.status_code == 201:
        return r.json()
    else:
        return None

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

def delete_event(calendar_key, event_id, event_version):
    url = "https://api.teamup.com/%s/events/%s?version=%s&redit=all" % (calendar_key, event_id, event_version)
    headers = {"Teamup-Token": cfg.teamup_apikey}

    r = requests.delete(url, headers=headers)
    return(r.status_code)

def edit_event(calendar_key, subcalendar_id, event_id, event_version, new_start, new_end, new_title):
    url = "https://api.teamup.com/%s/events/%s" % (calendar_key, event_id)
    headers = {"Teamup-Token": cfg.teamup_apikey, 
               "Content-type": "application/json"}

    payload = {
        "id": event_id,
        "subcalendar_id": subcalendar_id,
        "start_dt": new_start,
        "end_dt": new_end,
        "all_day": "false",
        "rrule": "",
        "title": new_title,
        "who": "",
        "location": "",
        "notes": "",
        "version": event_version,
        "redit": "null",
    }

    print(payload)

    r = requests.put(url, headers=headers, json=payload)
    return(r.json())

def get_changed_events(calendar_key, timestamp=""):
    url = "https://api.teamup.com/%s/events?modifiedSince=%s" % (calendar_key, timestamp)
    headers = {"Teamup-Token": cfg.teamup_apikey, 
               "Content-type": "application/json"}

    r = requests.get(url, headers=headers)
    return(r.json())

def get_events_between_dates(calendar_key, startDate, endDate, subcalendar):
    url = "https://api.teamup.com/%s/events?startDate=%s&endDate=%s&subcalendarId[]=%s" % (calendar_key, startDate, endDate, subcalendar)

    headers = {"Teamup-Token": cfg.teamup_apikey, 
               "Content-type": "application/json"}

    r = requests.get(url, headers=headers)
    return(r.json())