# google_calendar.py
from .models import Bookings
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow

scopes=['https://www.googleapis.com/auth/calendar']
credentials=pickle.load(open(r"C:\Users\DELL\intern_project\token.pkl","rb"))
service = build("calendar", "v3", credentials=credentials) 
result=service.calendarList().list().execute()
calendar_id=result['items'][0]['id']

def create_event(location,start_timing,end_timing,participants_emails,booking):    
    # Create a list of attendees using participants_emails
    attendees = [{"email": email} for email in participants_emails]
    event = {
                          'summary': 'Meeting',
                          'location': location,
                          'start': {'dateTime': start_timing, 'timeZone': 'Asia/Kolkata'},
                          'end': {'dateTime': end_timing, 'timeZone': 'Asia/Kolkata'},
                          'attendees': attendees
                         }
    # Get the event ID from the Google Calendar response
    result=service.events().insert(calendarId=calendar_id, body=event).execute()
    google_calendar_event_id = result['id']
    # Update the booking's google_calendar_event_id
    booking.google_calendar_event_id = google_calendar_event_id
    booking.save()

    return result
                
def event_addition(event_id,participant_email,booking):
    event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
    event['attendees'].append({"email": participant_email})
    
    updated_event = service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()
    booking.google_calendar_event_id = updated_event['id']
    booking.save()
    return updated_event

def event_removal(event_id, participant_email,booking):
    event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
    event['attendees'] = [attendee for attendee in event['attendees'] if attendee['email'] != participant_email]

    updated_event = service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()
    booking.google_calendar_event_id = updated_event['id']
    booking.save()
    return updated_event

def update_event(event_id,location,start_timing, end_timing,booking):
    event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()

    # Update event details
    event['location'] = location
    event['start']['dateTime'] = start_timing
    event['end']['dateTime'] = end_timing

    updated_event = service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()
    # Update the Google Calendar event ID in the booking
    booking.google_calendar_event_id = updated_event['id']
    booking.save()
    return updated_event

