import os
import datetime
from firecrawl import FirecrawlApp
from icalendar import Calendar, Event

# Firecrawl API-Key aus den GitHub Secrets auslesen
FIRECRAWL_API_KEY = os.environ.get("FIRECRAWL_API_KEY")

# Liste der zu scrapenden Promoter/Locations
PROMOTERS = [
    {"name": "Greyzone Concerts", "url": "https://www.greyzone-concerts.de"},
    {"name": "Puschen", "url": "https://puschen.net/berlin/"},
    {"name": "Trinity Music", "url": "https://trinitymusic.de"},
    {"name": "Sound of Liberation", "url": "https://soundofliberation.com"},
]

def generate_ical(events):
    cal = Calendar()
    cal.add('prodid', '-//Berlin Concert Aggregator//NONSGML v1.0//EN')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', 'Berlin Concerts Combined')

    for ev in events:
        event = Event()
        event.add('summary', ev.get('title', 'Konzert'))
        
        # Datum parsen (Standard: UTC-Setzung für Ganztag/Startzeit)
        start_date = ev.get('date')
        if isinstance(start_date, str):
            try:
                dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
                event.add('dtstart', dt.date())
            except ValueError:
                continue
        
        event.add('location', ev.get('location', 'Berlin'))
        event.add('description', f"Veranstalter: {ev.get('promoter')} | Info: {ev.get('url')}")
        cal.add_component(event)

    with open("combined_events.ics", "wb") as f:
        f.write(cal.to_ical())

def main():
    if not FIRECRAWL_API_KEY:
        print("Fehler: FIRECRAWL_API_KEY nicht gesetzt.")
        return

    app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
    all_events = []

    # Schema für strukturiertes Firecrawl JSON-Extracting
    schema = {
        "type": "object",
        "properties": {
            "events": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "date": {"type": "string", "description": "YYYY-MM-DD"},
                        "location": {"type": "string"}
                    },
                    "required": ["title", "date"]
                }
            }
        }
    }

    for promoter in PROMOTERS:
        try:
            print(f"Scrape {promoter['name']}...")
            data = app.scrape_url(promoter['url'], params={'formats': ['extract'], 'extract': {'schema': schema}})
            extracted = data.get('extract', {}).get('events', [])
            for e in extracted:
                e['promoter'] = promoter['name']
                e['url'] = promoter['url']
                all_events.append(e)
        except Exception as err:
            print(f"Fehler bei {promoter['name']}: {err}")

    generate_ical(all_events)
    print(f"{len(all_events)} Events in combined_events.ics gespeichert.")

if __name__ == "__main__":
    main()
