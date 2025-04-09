"""
NOTE: This is a work-in-progress!!


"""

import pandas as pd
from icalendar import Calendar, Event
from datetime import datetime
import pytz
from uuid import uuid4


def event_conversion(csv_fp):

    # Load your updated CSV
    df = pd.read_csv("consultant_meetings_schedule_updated.csv")

    # Set timezone
    cst = pytz.timezone("US/Central")

    # Create iCalendar object
    cal = Calendar()
    cal.add('prodid', '-//Financial Consultant Meetings//example.com//')
    cal.add('version', '2.0')

    # Generate events
    for _, row in df.iterrows():
        event = Event()
        event.add('summary', row['Subject'])
        start_dt = cst.localize(datetime.strptime(f"{row['Start Date']} {row['Start Time']}", "%Y-%m-%d %H:%M"))
        end_dt = cst.localize(datetime.strptime(f"{row['End Date']} {row['End Time']}", "%Y-%m-%d %H:%M"))
        event.add('dtstart', start_dt)
        event.add('dtend', end_dt)
        event.add('location', row['Location'])
        event.add('description', row['Description'])
        event['uid'] = str(uuid4())
        cal.add_component(event)

    return cal

def write_cal_to_file(cal):
    # Write to .ics file
    with open("consultant_meetings_schedule.ics", "wb") as f:
        f.write(cal.to_ical())
