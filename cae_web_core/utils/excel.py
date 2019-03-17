import datetime
import logging
import re

import xlrd

from ..models import RoomEvent


logger = logging.getLogger(__name__)

RE_ROOM = re.compile(r'([A-Za-z])-?(\d+)') # E.g. C204, C-204
RE_WEEKDAY = re.compile(r'(Mon)|(Tue)|(Wed)|(Thu)|(Fri)|(Sat)|(Sun)')

def parse_room(value):
    if not value:
        return None

    match = RE_ROOM.search(value)
    if match:
        letter, number = match.groups()
        return '{0}-{1}'.format(letter, number)

    return None

def parse_weekday(value):
    if not value:
        return None

    match = RE_WEEKDAY.search(value)
    if match:
        # Return index of first True value, plus 1 to calculate ISO weekday
        return [i for i, x in enumerate(match.groups()) if x][0] + 1

    return None

def add_minutes(time_obj, minutes):
    """Add minutes to time_obj by only updating hours and minutes.

    NOTE: This will not increase the day if adding to a time just before
    midnight. It will instead 'wrap around'."""
    new_minutes = time_obj.minute + minutes
    hours = int(new_minutes / 60)
    new_minutes -= hours * 60
    new_hours = (time_obj.hour + hours) % 24 # Wrap around near midnight

    time_obj = time_obj.replace(hour=new_hours, minute=new_minutes)

    return time_obj


def upload_room_schedule(schedule_data):
    """Parse an .xls or .xlsx file for events.

    There is no standard for the files, so we make the following assumptions:

    - Rooms are above events and in the form [letter][optional dash][numbers]
      and may have extra text. E.g. 'C204(stuff)' -> 'C-204'
    - Days are above/left of events. We only check for weekday abbreviations to
      determine if this is a weekday field. E.g. Mon, Tue, Wed, etc.
    - Times are left of events and are marked as dates/times in excel. We can't
      assume AM or PM is correct, so we use context to assume later times are PM
      for a given day.
    - Cells with contents that have a room, day and time are assumed to be
      events. If the contents are repeated contigously in the column, one event
      will be created that starts at the first row time, and ends at the last
      row time + 30 minutes.

    Here is one such example that satifies the above conditions:

        Mon.    C-208       C209(computer)
        8:30    Event 1     Event 2
        9:00    Event 1     Event 2
        12:00               Event 2
        12:30   Event 1

    which will be parsed into 3 separate events for Monday.

        Event 1 (A):
            Room:      C-208
            Start:   8:30 AM
            End:     9:30 AM
        Event 1 (B):
            Room:      C-208
            Start:  12:30 PM
            End:     1:00 PM
        Event 2:
            Room:      C-209
            Start:   8:30 AM
            End:    12:30 PM
    """
    book = xlrd.open_workbook(file_contents=schedule_data)
    logger.info("Reading %s", book)

    sheet = book.sheet_by_index(0)

    current_room = {} # column: room
    current_weekday = None # ISO Weekday, 1=Monday, 7=Sunday

    events = {} # (weekday, col, name): [{start: time, end: time, last_row: 1}]

    time_am = True
    last_event_time = None

    for row in range(sheet.nrows):
        event_time = None
        for col in range(sheet.ncols):
            cell = sheet.cell(row, col)
            if not str(cell.value or '').strip():
                continue

            value = str(cell.value).strip()
            if cell.ctype == xlrd.XL_CELL_DATE:
                year, month, day, hour, minute, second = xlrd.xldate_as_tuple(cell.value, book.datemode)
                if year == month == day == 0:
                    # The hour in excel may be stored as AM, when it should be PM.
                    # Keep track of each weekday and change to PM when it suddenly
                    # gets a lower value (11 AM -> 1 AM, guess 1 PM)
                    if last_event_time and time_am and hour < last_event_time.hour:
                        time_am = False
                        #logger.info("SWITCHING TO PM")

                    if not time_am and hour < 12 or (hour == 12 and minute == 0):
                        hour += 12
                        hour = hour % 24

                    event_time = datetime.time(hour=hour, minute=minute)
                    last_event_time = event_time

                    #logger.info("%s:%s", hour, minute)
                    continue
            elif not event_time:
                # Don't check for weekday or room headers if already have event_time

                # Check for weekday
                weekday = parse_weekday(value)
                if weekday and weekday != current_weekday:
                    current_weekday = weekday
                    #logger.info("WEEKDAY CHANGE TO %d", current_weekday)
                    #logger.info("SWITCHING TO AM")
                    time_am = True # New day started, so go back to AM
                    last_event_time = None
                    continue

                # Check for room
                room = parse_room(value)
                if room:
                    current_room[col] = room
                    continue

            room = current_room.get(col)

            if event_time and room and current_weekday:
                #logger.info("(%d, %s, %s): %s", current_weekday, room, event_time, value)

                key = (current_weekday, col, value)
                day_events = events.get(key)

                new_event = {
                    'start': event_time,
                    'end': add_minutes(event_time, 30),
                    'last_row': row,
                }

                if day_events:
                    event = day_events[-1]
                    # update event if still one continuous block
                    if row == event['last_row'] + 1:
                        # Same event
                        event['end'] = new_event['end']
                        event['last_row'] = new_event['last_row']
                    else:
                        # Different event in same weekday
                        day_events.append(new_event)
                else:
                    events[key] = [new_event]

    # TODO: Conslidate events that are the same across multiple days, using
    # RecurrentRules.

    from pprint import pprint
    pprint(events)

    return events
