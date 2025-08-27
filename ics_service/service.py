import os
from ics import Calendar, Event
from ics.grammar.parse import ContentLine
from datetime import datetime


def create_event(meeting_request):
    e = Event()
    c = Calendar()

    event_name = 'Meeting with \nSeniWave'
    meeting_date = meeting_request.calendar_day.date
    meeting_id = meeting_request.id
    meet_code = meeting_request.meet_code

    start_datetime = datetime.combine(
        meeting_date, 
        datetime.min.time().replace(hour=meeting_request.time_span.start // 60, minute=meeting_request.time_span.start % 60)
    )
    end_datetime = datetime.combine(
        meeting_date, 
        datetime.min.time().replace(hour=meeting_request.time_span.end // 60, minute=meeting_request.time_span.end % 60)
    )
    
    e.name = event_name
    e.begin = start_datetime
    e.end = end_datetime
    e.description = f'''
        You successfully booked meeting with SeniWave.
        Join meeting: https://meet.seniwave.com/rooms/{meet_code}
        About meeting, Cancel and more: https://meet.seniwave.com/{meeting_id}
    '''

    e.extra.append(ContentLine(name="URL", value=f"https://meet.seniwave.com/rooms/{meet_code}"))
    e.extra.append(ContentLine(name="LOCATION", value="Online Meeting"))
    e.extra.append(ContentLine(name="STATUS", value="CONFIRMED"))
    e.extra.append(ContentLine(name="TRANSP", value="OPAQUE"))
    # e.extra.append(ContentLine(name="PRIORITY", value="5"))
    
    e.extra.append(ContentLine(name="BEGIN", value="VALARM"))
    e.extra.append(ContentLine(name="ACTION", value="DISPLAY"))
    e.extra.append(ContentLine(name="DESCRIPTION", value="Meeting starts in 15 minutes"))
    e.extra.append(ContentLine(name="TRIGGER", value="-PT15M"))
    e.extra.append(ContentLine(name="END", value="VALARM"))

    c.events.add(e)

    save_event_to_file(c, f'{meeting_id}.ics')

    return c

def save_event_to_file(event, filename):
    os.makedirs('ics_files', exist_ok=True)
    filepath = os.path.join('ics_service/events', filename)
    with open(filepath, 'w', encoding='utf-8') as my_file:
        my_file.writelines(event.serialize_iter())