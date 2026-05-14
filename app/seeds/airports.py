"""
Seed script — populates the airports table with major world airports.
Run with: docker exec -it skymind_api python -m app.seeds.airports
"""

from app.database import SessionLocal
from app.models.airport import Airport


AIRPORTS = [
    # Middle East
    ("DXB", "Dubai International Airport",          "Dubai",         "AE", 25.252778,  55.364444,  "Asia/Dubai",       True),
    ("AUH", "Abu Dhabi International Airport",       "Abu Dhabi",     "AE", 24.432972,  54.651138,  "Asia/Dubai",       True),
    ("DOH", "Hamad International Airport",           "Doha",          "QA", 25.273056,  51.608056,  "Asia/Qatar",       True),
    ("RUH", "King Khalid International Airport",     "Riyadh",        "SA", 24.957674,  46.698776,  "Asia/Riyadh",      True),
    ("KWI", "Kuwait International Airport",          "Kuwait City",   "KW", 29.226650,  47.968900,  "Asia/Kuwait",      False),
    ("MCT", "Muscat International Airport",          "Muscat",        "OM", 23.593300,  58.284400,  "Asia/Muscat",      False),

    # Europe
    ("LHR", "Heathrow Airport",                      "London",        "GB", 51.477500,  -0.461389,  "Europe/London",    True),
    ("CDG", "Charles de Gaulle Airport",             "Paris",         "FR", 49.009722,   2.547778,  "Europe/Paris",     True),
    ("FRA", "Frankfurt Airport",                     "Frankfurt",     "DE", 50.033333,   8.570556,  "Europe/Berlin",    True),
    ("AMS", "Amsterdam Airport Schiphol",            "Amsterdam",     "NL", 52.308613,   4.763889,  "Europe/Amsterdam", True),
    ("MAD", "Adolfo Suárez Madrid–Barajas Airport",  "Madrid",        "ES", 40.493556,  -3.566764,  "Europe/Madrid",    True),
    ("BCN", "Barcelona–El Prat Airport",             "Barcelona",     "ES", 41.296944,   2.078333,  "Europe/Madrid",    True),
    ("FCO", "Leonardo da Vinci International",       "Rome",          "IT", 41.800278,  12.238889,  "Europe/Rome",      True),
    ("IST", "Istanbul Airport",                      "Istanbul",      "TR", 41.275278,  28.751944,  "Europe/Istanbul",  True),
    ("MUC", "Munich Airport",                        "Munich",        "DE", 48.353783,  11.786086,  "Europe/Berlin",    True),
    ("ZRH", "Zurich Airport",                        "Zurich",        "CH", 47.464722,   8.549167,  "Europe/Zurich",    False),
    ("VIE", "Vienna International Airport",          "Vienna",        "AT", 48.110278,  16.569722,  "Europe/Vienna",    False),
    ("CPH", "Copenhagen Airport",                    "Copenhagen",    "DK", 55.617917,  12.655972,  "Europe/Copenhagen",False),

    # Asia
    ("SIN", "Singapore Changi Airport",              "Singapore",     "SG",  1.359167, 103.989444,  "Asia/Singapore",   True),
    ("BKK", "Suvarnabhumi Airport",                  "Bangkok",       "TH", 13.681108, 100.747283,  "Asia/Bangkok",     True),
    ("HKG", "Hong Kong International Airport",       "Hong Kong",     "HK", 22.308919, 113.914603,  "Asia/Hong_Kong",   True),
    ("NRT", "Narita International Airport",          "Tokyo",         "JP", 35.764722, 140.386389,  "Asia/Tokyo",       True),
    ("ICN", "Incheon International Airport",         "Seoul",         "KR", 37.469075, 126.450517,  "Asia/Seoul",       True),
    ("KUL", "Kuala Lumpur International Airport",    "Kuala Lumpur",  "MY",  2.745578, 101.709917,  "Asia/Kuala_Lumpur",True),
    ("DEL", "Indira Gandhi International Airport",   "New Delhi",     "IN", 28.556555,  77.100956,  "Asia/Kolkata",     True),
    ("BOM", "Chhatrapati Shivaji Maharaj Airport",   "Mumbai",        "IN", 19.088700,  72.867900,  "Asia/Kolkata",     True),
    ("PEK", "Beijing Capital International Airport", "Beijing",       "CN", 40.080111, 116.584556,  "Asia/Shanghai",    True),
    ("PVG", "Shanghai Pudong International Airport", "Shanghai",      "CN", 31.143378, 121.805214,  "Asia/Shanghai",    True),
    ("MNL", "Ninoy Aquino International Airport",    "Manila",        "PH", 14.508647, 121.019581,  "Asia/Manila",      False),
    ("CGK", "Soekarno-Hatta International Airport",  "Jakarta",       "ID", -6.125567, 106.655897,  "Asia/Jakarta",     False),

    # Americas
    ("JFK", "John F. Kennedy International Airport", "New York",      "US", 40.639722, -73.778889,  "America/New_York", True),
    ("LAX", "Los Angeles International Airport",     "Los Angeles",   "US", 33.942536,-118.408048,  "America/Los_Angeles",True),
    ("ORD", "O'Hare International Airport",          "Chicago",       "US", 41.978603, -87.904842,  "America/Chicago",  True),
    ("MIA", "Miami International Airport",           "Miami",         "US", 25.795865, -80.287046,  "America/New_York", True),
    ("SFO", "San Francisco International Airport",   "San Francisco", "US", 37.618972,-122.374889,  "America/Los_Angeles",True),
    ("YYZ", "Toronto Pearson International Airport", "Toronto",       "CA", 43.677222, -79.630556,  "America/Toronto",  True),
    ("GRU", "São Paulo/Guarulhos Airport",           "São Paulo",     "BR",-23.431944, -46.469444,  "America/Sao_Paulo",True),
    ("EZE", "Ministro Pistarini International",      "Buenos Aires",  "AR",-34.822222, -58.535833,  "America/Argentina/Buenos_Aires", False),
    ("MEX", "Mexico City International Airport",     "Mexico City",   "MX", 19.436303, -99.072097,  "America/Mexico_City", True),
    ("BOG", "El Dorado International Airport",       "Bogotá",        "CO",  4.701594, -74.146947,  "America/Bogota",   False),

    # Africa & Oceania
    ("JNB", "O.R. Tambo International Airport",      "Johannesburg",  "ZA",-26.133694,  28.242317,  "Africa/Johannesburg", True),
    ("CAI", "Cairo International Airport",           "Cairo",         "EG", 30.121944,  31.405556,  "Africa/Cairo",     True),
    ("CMN", "Mohammed V International Airport",      "Casablanca",    "MA", 33.367500,  -7.589970,  "Africa/Casablanca",False),
    ("NBO", "Jomo Kenyatta International Airport",   "Nairobi",       "KE", -1.319167,  36.927500,  "Africa/Nairobi",   False),
    ("SYD", "Sydney Kingsford Smith Airport",        "Sydney",        "AU",-33.946111, 151.177222,  "Australia/Sydney", True),
    ("MEL", "Melbourne Airport",                     "Melbourne",     "AU",-37.673333, 144.843333,  "Australia/Melbourne",True),
    ("AKL", "Auckland Airport",                      "Auckland",      "NZ",-37.008056, 174.791667,  "Pacific/Auckland", False),
]


def seed_airports():
    db = SessionLocal()
    try:
        existing = db.query(Airport).count()
        if existing > 0:
            print(f"Airports table already has {existing} records — skipping seed.")
            return

        airports = [
            Airport(
                iata_code=iata,
                name=name,
                city=city,
                country_code=country,
                latitude=lat,
                longitude=lon,
                timezone=tz,
                is_major=is_major,
            )
            for iata, name, city, country, lat, lon, tz, is_major in AIRPORTS
        ]

        db.add_all(airports)
        db.commit()
        print(f"Successfully seeded {len(airports)} airports.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding airports: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_airports()