"""
Mock Amadeus Flight Inspiration API client.
Returns up to 50 destination candidates from a given origin.
Swap-ready: set AMADEUS_MOCK=false in .env and implement _real_fetch()
to hit the live endpoint with zero changes to callers.
"""
from __future__ import annotations

import os
import random
from typing import Any

_DESTINATIONS: list[dict[str, Any]] = [
    {"iata": "BKK", "city": "Bangkok",         "country": "Thailand",       "base_price": 210, "duration_min": 390,  "region": "Asia"},
    {"iata": "KUL", "city": "Kuala Lumpur",    "country": "Malaysia",       "base_price": 195, "duration_min": 420,  "region": "Asia"},
    {"iata": "SIN", "city": "Singapore",       "country": "Singapore",      "base_price": 230, "duration_min": 430,  "region": "Asia"},
    {"iata": "MNL", "city": "Manila",          "country": "Philippines",    "base_price": 270, "duration_min": 480,  "region": "Asia"},
    {"iata": "CGK", "city": "Jakarta",         "country": "Indonesia",      "base_price": 255, "duration_min": 460,  "region": "Asia"},
    {"iata": "HKG", "city": "Hong Kong",       "country": "Hong Kong",      "base_price": 340, "duration_min": 480,  "region": "Asia"},
    {"iata": "PEK", "city": "Beijing",         "country": "China",          "base_price": 390, "duration_min": 510,  "region": "Asia"},
    {"iata": "PVG", "city": "Shanghai",        "country": "China",          "base_price": 380, "duration_min": 495,  "region": "Asia"},
    {"iata": "ICN", "city": "Seoul",           "country": "South Korea",    "base_price": 410, "duration_min": 510,  "region": "Asia"},
    {"iata": "NRT", "city": "Tokyo",           "country": "Japan",          "base_price": 480, "duration_min": 540,  "region": "Asia"},
    {"iata": "DEL", "city": "New Delhi",       "country": "India",          "base_price": 140, "duration_min": 195,  "region": "South Asia"},
    {"iata": "BOM", "city": "Mumbai",          "country": "India",          "base_price": 130, "duration_min": 185,  "region": "South Asia"},
    {"iata": "MAA", "city": "Chennai",         "country": "India",          "base_price": 125, "duration_min": 200,  "region": "South Asia"},
    {"iata": "HYD", "city": "Hyderabad",       "country": "India",          "base_price": 120, "duration_min": 190,  "region": "South Asia"},
    {"iata": "CMB", "city": "Colombo",         "country": "Sri Lanka",      "base_price": 115, "duration_min": 215,  "region": "South Asia"},
    {"iata": "KTM", "city": "Kathmandu",       "country": "Nepal",          "base_price": 200, "duration_min": 270,  "region": "South Asia"},
    {"iata": "DAC", "city": "Dhaka",           "country": "Bangladesh",     "base_price": 175, "duration_min": 300,  "region": "South Asia"},
    {"iata": "LHR", "city": "London",          "country": "UK",             "base_price": 430, "duration_min": 430,  "region": "Europe"},
    {"iata": "CDG", "city": "Paris",           "country": "France",         "base_price": 440, "duration_min": 425,  "region": "Europe"},
    {"iata": "AMS", "city": "Amsterdam",       "country": "Netherlands",    "base_price": 420, "duration_min": 420,  "region": "Europe"},
    {"iata": "FCO", "city": "Rome",            "country": "Italy",          "base_price": 390, "duration_min": 380,  "region": "Europe"},
    {"iata": "BCN", "city": "Barcelona",       "country": "Spain",          "base_price": 385, "duration_min": 400,  "region": "Europe"},
    {"iata": "MAD", "city": "Madrid",          "country": "Spain",          "base_price": 380, "duration_min": 410,  "region": "Europe"},
    {"iata": "FRA", "city": "Frankfurt",       "country": "Germany",        "base_price": 410, "duration_min": 415,  "region": "Europe"},
    {"iata": "VIE", "city": "Vienna",          "country": "Austria",        "base_price": 400, "duration_min": 405,  "region": "Europe"},
    {"iata": "ZRH", "city": "Zurich",          "country": "Switzerland",    "base_price": 450, "duration_min": 420,  "region": "Europe"},
    {"iata": "IST", "city": "Istanbul",        "country": "Turkey",         "base_price": 180, "duration_min": 215,  "region": "Europe"},
    {"iata": "ATH", "city": "Athens",          "country": "Greece",         "base_price": 310, "duration_min": 290,  "region": "Europe"},
    {"iata": "PRG", "city": "Prague",          "country": "Czech Republic", "base_price": 370, "duration_min": 380,  "region": "Europe"},
    {"iata": "WAW", "city": "Warsaw",          "country": "Poland",         "base_price": 350, "duration_min": 360,  "region": "Europe"},
    {"iata": "CAI", "city": "Cairo",           "country": "Egypt",          "base_price": 120, "duration_min": 175,  "region": "Africa"},
    {"iata": "CMN", "city": "Casablanca",      "country": "Morocco",        "base_price": 250, "duration_min": 395,  "region": "Africa"},
    {"iata": "NBO", "city": "Nairobi",         "country": "Kenya",          "base_price": 280, "duration_min": 330,  "region": "Africa"},
    {"iata": "ADD", "city": "Addis Ababa",     "country": "Ethiopia",       "base_price": 260, "duration_min": 310,  "region": "Africa"},
    {"iata": "JNB", "city": "Johannesburg",    "country": "South Africa",   "base_price": 350, "duration_min": 480,  "region": "Africa"},
    {"iata": "LOS", "city": "Lagos",           "country": "Nigeria",        "base_price": 390, "duration_min": 420,  "region": "Africa"},
    {"iata": "JFK", "city": "New York",        "country": "USA",            "base_price": 680, "duration_min": 840,  "region": "Americas"},
    {"iata": "LAX", "city": "Los Angeles",     "country": "USA",            "base_price": 720, "duration_min": 960,  "region": "Americas"},
    {"iata": "ORD", "city": "Chicago",         "country": "USA",            "base_price": 660, "duration_min": 870,  "region": "Americas"},
    {"iata": "YYZ", "city": "Toronto",         "country": "Canada",         "base_price": 650, "duration_min": 850,  "region": "Americas"},
    {"iata": "GRU", "city": "Sao Paulo",       "country": "Brazil",         "base_price": 720, "duration_min": 1080, "region": "Americas"},
    {"iata": "EZE", "city": "Buenos Aires",    "country": "Argentina",      "base_price": 750, "duration_min": 1020, "region": "Americas"},
    {"iata": "MEX", "city": "Mexico City",     "country": "Mexico",         "base_price": 700, "duration_min": 930,  "region": "Americas"},
    {"iata": "BOG", "city": "Bogota",          "country": "Colombia",       "base_price": 710, "duration_min": 960,  "region": "Americas"},
    {"iata": "SYD", "city": "Sydney",          "country": "Australia",      "base_price": 580, "duration_min": 840,  "region": "Oceania"},
    {"iata": "MEL", "city": "Melbourne",       "country": "Australia",      "base_price": 590, "duration_min": 855,  "region": "Oceania"},
    {"iata": "AKL", "city": "Auckland",        "country": "New Zealand",    "base_price": 620, "duration_min": 930,  "region": "Oceania"},
    {"iata": "TLV", "city": "Tel Aviv",        "country": "Israel",         "base_price": 220, "duration_min": 250,  "region": "Middle East"},
    {"iata": "AMM", "city": "Amman",           "country": "Jordan",         "base_price": 150, "duration_min": 185,  "region": "Middle East"},
    {"iata": "MCT", "city": "Muscat",          "country": "Oman",           "base_price": 90,  "duration_min": 105,  "region": "Middle East"},
]

_MOCK = os.getenv("AMADEUS_MOCK", "true").lower() != "false"


def _add_jitter(base: float, pct: float = 0.12) -> float:
    delta = base * pct
    return round(base + random.uniform(-delta, delta), 2)


def get_inspiration(origin_iata: str, max_results: int = 50) -> list[dict[str, Any]]:
    """
    Return destination candidate dicts for the given origin.
    Each dict: iata, city, country, region, price_usd, duration_min.
    Swap path: replace _mock_fetch body with real Amadeus HTTP call.
    """
    if _MOCK:
        return _mock_fetch(origin_iata, max_results)
    return _real_fetch(origin_iata, max_results)  # pragma: no cover


def _mock_fetch(origin_iata: str, max_results: int) -> list[dict[str, Any]]:
    results = []
    for dest in _DESTINATIONS[:max_results]:
        if dest["iata"] == origin_iata.upper():
            continue
        results.append({
            "iata": dest["iata"],
            "city": dest["city"],
            "country": dest["country"],
            "region": dest["region"],
            "price_usd": _add_jitter(dest["base_price"]),
            "duration_min": dest["duration_min"],
        })
    return results


def _real_fetch(origin_iata: str, max_results: int) -> list[dict[str, Any]]:  # pragma: no cover
    """
    TODO: implement when Amadeus self-service is available.
    Endpoint: GET /v1/shopping/flight-destinations
    Params:   origin=<iata>, maxPrice=<budget>
    Auth:     Bearer token from /v1/security/oauth2/token
    """
    raise NotImplementedError("Real Amadeus fetch not yet implemented")