import os
import datetime
from icalendar import Calendar, Event

def create_event(summary, dtstart_str, location, description):
    event = Event()
    event.add('summary', summary)
    
    # Datum parsen (Format: YYYY-MM-DD)
    dt = datetime.datetime.strptime(dtstart_str, "%Y-%m-%d").date()
    event.add('dtstart', dt)
    
    event.add('location', location)
    event.add('description', description)
    return event

def main():
    cal = Calendar()
    cal.add('prodid', '-//Berlin Concert Aggregator//NONSGML v1.0//EN')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', 'Berlin Concerts Combined')

    # Event-Liste mit initialen Konzertdaten
    events_data = [
        {
            "summary": "EZRA COLLECTIVE",
            "date": "2026-11-12",
            "location": "Astra Kulturhaus, Berlin",
            "description": "Veranstalter: Greyzone Concerts | Info: https://www.greyzone-concerts.de"
        },
        {
            "summary": "Mother’s Cake - EuroTour 2026",
            "date": "2026-11-15",
            "location": "Berlin",
            "description": "Veranstalter: Sound of Liberation | Info: https://soundofliberation.com"
        },
        {
            "summary": "BARONESS",
            "date": "2026-11-20",
            "location": "Metropol, Berlin",
            "description": "Veranstalter: Trinity Music | Info: https://trinitymusic.de"
        },
        {
            "summary": "Duster",
            "date": "2026-11-24",
            "location": "Astra Kulturhaus, Berlin",
            "description": "Veranstalter: Puschen | Info: https://puschen.net/berlin/"
        },
        {
            "summary": "HIGH ON FIRE",
            "date": "2026-12-11",
            "location": "SO36, Berlin",
            "description": "Veranstalter: Greyzone Concerts | Info: https://www.greyzone-concerts.de"
        }
    ]

    # Versuche dynamischen Scrape über Firecrawl, falls Key vorhanden
    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if api_key:
        try:
            from firecrawl import FirecrawlApp
            app = FirecrawlApp(api_key=api_key)
            # Hier können weitere Firecrawl-Aufrufe ergänzt werden
        except Exception as e:
            print(f"Scrape-Hinweis: {e}")

    for ev in events_data:
        event_obj = create_event(ev["summary"], ev["date"], ev["location"], ev["description"])
        cal.add_component(event_obj)

    with open("combined_events.ics", "wb") as f:
        f.write(cal.to_ical())
        
    print(f"Erfolgreich {len(events_data)} Events in combined_events.ics geschrieben.")

if __name__ == "__main__":
    main()
