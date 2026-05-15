"""
Amadeus Client — Mock Implementation
=====================================
Interface matches the real Amadeus Flight Offers Search API response shape exactly.
To plug in a real provider later:
  1. Set AMADEUS_MOCK=false in .env
  2. Replace _real_search() with actual HTTP call
  3. Zero changes needed in flight_service.py or above

Mock data uses realistic prices, durations, and airline codes for DXB-based routes.
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.config import get_settings

settings = get_settings()


def _make_segment(
    origin: str,
    destination: str,
    departure_dt: str,
    duration_minutes: int,
    flight_number: str,
    carrier: str,
) -> Dict[str, Any]:
    dep = datetime.fromisoformat(departure_dt)
    arr = dep + timedelta(minutes=duration_minutes)
    return {
        "departure": {
            "iataCode": origin,
            "at": dep.isoformat(),
        },
        "arrival": {
            "iataCode": destination,
            "at": arr.isoformat(),
        },
        "carrierCode": carrier,
        "number": flight_number,
        "duration": f"PT{duration_minutes // 60}H{duration_minutes % 60}M",
        "numberOfStops": 0,
    }


def _make_offer(
    offer_id: str,
    origin: str,
    destination: str,
    departure_date: str,
    passengers: int,
    price_usd: float,
    segments: List[Dict],
    total_duration_minutes: int,
    cabin_class: str = "ECONOMY",
) -> Dict[str, Any]:
    total_duration = f"PT{total_duration_minutes // 60}H{total_duration_minutes % 60}M"
    return {
        "id": offer_id,
        "source": "MOCK",
        "itineraries": [
            {
                "duration": total_duration,
                "segments": segments,
            }
        ],
        "price": {
            "currency": "USD",
            "total": str(round(price_usd * passengers, 2)),
            "base": str(round(price_usd * passengers * 0.82, 2)),
            "per_passenger": str(round(price_usd, 2)),
        },
        "travelerPricings": [
            {
                "travelerId": str(i + 1),
                "fareOption": "STANDARD",
                "travelerType": "ADULT",
                "price": {"currency": "USD", "total": str(round(price_usd, 2))},
                "fareDetailsBySegment": [
                    {"cabin": cabin_class, "class": cabin_class[0]}
                    for _ in segments
                ],
            }
            for i in range(passengers)
        ],
        "numberOfBookableSeats": random.randint(2, 9),
        "cabin_class": cabin_class,
    }


def _mock_search(
    origin: str,
    destination: str,
    departure_date: str,
    passengers: int,
    cabin_class: str,
) -> List[Dict[str, Any]]:
    """
    Returns 8 realistic mock flight offers.
    Prices and durations vary enough to make the scoring engine interesting.
    """
    dep_base = f"{departure_date}T06:00:00"
    offers = []

    # Airline profiles: (carrier_code, name, base_price_usd, duration_minutes)
    airlines = [
        ("EK", "Emirates",        420, 420),   # 7h direct
        ("EK", "Emirates",        390, 420),   # cheaper EK flight
        ("FZ", "flydubai",        280, 480),   # 8h with stop in SHJ
        ("QR", "Qatar Airways",   380, 510),   # 8h30m via DOH
        ("EY", "Etihad",          360, 495),   # 8h15m via AUH
        ("G9", "Air Arabia",      210, 570),   # 9h30m budget
        ("WY", "Oman Air",        340, 525),   # 8h45m via MCT
        ("SV", "Saudia",          310, 540),   # 9h via RUH
    ]

    for i, (carrier, _, base_price, duration) in enumerate(airlines):
        # Add small random variation so prices aren't perfectly flat
        price = base_price + random.uniform(-15, 15)
        price = max(150, round(price, 2))

        dep_hour = 6 + (i * 2)
        dep_hour = dep_hour % 24
        dep_dt = f"{departure_date}T{dep_hour:02d}:00:00"

        is_direct = duration <= 430
        if is_direct:
            segments = [_make_segment(origin, destination, dep_dt, duration, f"{carrier}{1000 + i}", carrier)]
        else:
            # Add a stopover segment
            stop_map = {
                "FZ": "SHJ", "QR": "DOH", "EY": "AUH",
                "WY": "MCT", "SV": "RUH", "G9": "SHJ",
            }
            via = stop_map.get(carrier, "DOH")
            leg1_dur = duration // 2
            leg2_dur = duration - leg1_dur - 90  # 90 min ground time
            arr1_dt = (datetime.fromisoformat(dep_dt) + timedelta(minutes=leg1_dur)).isoformat()
            dep2_dt = (datetime.fromisoformat(arr1_dt) + timedelta(minutes=90)).isoformat()
            segments = [
                _make_segment(origin, via, dep_dt, leg1_dur, f"{carrier}{1000 + i}A", carrier),
                _make_segment(via, destination, dep2_dt, leg2_dur, f"{carrier}{1000 + i}B", carrier),
            ]

        offers.append(_make_offer(
            offer_id=f"mock-{i+1}",
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            passengers=passengers,
            price_usd=price,
            segments=segments,
            total_duration_minutes=duration,
            cabin_class=cabin_class,
        ))

    return offers


def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    passengers: int = 1,
    cabin_class: str = "ECONOMY",
) -> List[Dict[str, Any]]:
    """
    Public interface. flight_service.py calls only this function.
    AMADEUS_MOCK=true  → returns mock data (default for now)
    AMADEUS_MOCK=false → calls real Amadeus API (plug in later)
    """
    use_mock = getattr(settings, "AMADEUS_MOCK", "true").lower() != "false"

    if use_mock:
        return _mock_search(origin, destination, departure_date, passengers, cabin_class)

    # ── Real Amadeus call (wired up when AMADEUS_MOCK=false) ──────────────
    # import httpx
    # token = _get_amadeus_token()
    # response = httpx.post(
    #     "https://test.api.amadeus.com/v2/shopping/flight-offers",
    #     headers={"Authorization": f"Bearer {token}"},
    #     json={...},
    # )
    # return response.json()["data"]
    raise NotImplementedError("Real Amadeus integration not yet wired — set AMADEUS_MOCK=true")