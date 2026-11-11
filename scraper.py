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

    # Liste der zu scrapenden Promoter/Locations (inkl. Neue Zukunft)
    PROMOTERS = [
        {"name": "Greyzone Concerts", "url": "https://www.greyzone-concerts.de"},
        {"name": "Puschen", "url": "https://puschen.net/berlin/"},
        {"name": "Trinity Music", "url": "https://trinitymusic.de"},
        {"name": "Sound of Liberation", "url": "https://soundofliberation.com"},
        {"name": "Neue Zukunft", "url": "https://neue-zukunft.org/konzerte.html"},
    ]

    events_data = []

    # Versuche dynamischen Scrape über Firecrawl, falls Key vorhanden
    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if api_key:
        try:
            from firecrawl import FirecrawlApp
            app = FirecrawlApp(api_key=api_key)
            
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
                        events_data.append({
                            "summary": e.get('title', 'Konzert'),
                            "date": e.get('date'),
                            "location": e.get('location', promoter['name'] + ', Berlin'),
                            "description": f"Veranstalter/Location: {promoter['name']} | Info: {promoter['url']}"
                        })
                except Exception as err:
                    print(f"Fehler bei {promoter['name']}: {err}")

        except Exception as e:
            print(f"Firecrawl-Initialisierungsfehler: {e}")

    # Fallback / Test-Events falls noch keine dynamischen Daten zurückkommen
    if not events_data:
        events_data = [
            {
                "summary": "EZRA COLLECTIVE",
                "date": "2026-11-12",
                "location": "Astra Kulturhaus, Berlin",
                "description": "Veranstalter: Greyzone Concerts | Info: https://www.greyzone-concerts.de"
            },
            {
                "summary": "Live im Neue Zukunft",
                "date": "2026-11-18",
                "location": "Neue Zukunft, Berlin",
                "description": "Veranstalter: Neue Zukunft | Info: https://neue-zukunft.org/konzerte.html"
            }
        ]

    for ev in events_data:
        try:
            event_obj = create_event(ev["summary"], ev["date"], ev["location"], ev["description"])
            cal.add_component(event_obj)
        except Exception as ex:
            printスキip(f"Fehler beim Hinzufügen von Event {ev}: {ex}")

    with open("combined_events.ics", "wb") as f:
        f.write(cal.to_ical())
        
    print(f"Erfolgreich {len(events_data)} Events in combined_events.ics geschrieben.")

if __name__ == "__main__":
    main()
