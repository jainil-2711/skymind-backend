"""
Claude API client for AI trip planning.
Sends a natural language prompt and returns a structured list of itinerary legs
matching the ItineraryLeg schema used by the existing itinerary builder.

Swap-ready: set CLAUDE_MOCK=true in .env to use mock responses during development.
"""
from __future__ import annotations

import json
import os
from typing import Any

import httpx

CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL   = "claude-sonnet-4-20250514"
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")
MOCK           = True

SYSTEM_PROMPT = """You are a flight itinerary planner. Given a natural language trip request, return ONLY a valid JSON array of flight legs. No explanation, no markdown, no extra text — raw JSON only.

Each leg must follow this exact schema:
{
  "order": <integer starting at 1>,
  "origin_iata": <3-letter IATA code, uppercase>,
  "destination_iata": <3-letter IATA code, uppercase>,
  "depart_date": <"YYYY-MM-DD">,
  "cabin_class": <"ECONOMY" | "BUSINESS" | "FIRST">,
  "estimated_price_usd": <number>,
  "duration_min": <integer>
}

Rules:
- Always use real IATA codes
- depart_date must be a future date
- cabin_class default is ECONOMY unless specified
- estimated_price_usd and duration_min must be realistic estimates
- Return only the JSON array, nothing else
"""


def generate_itinerary(prompt: str) -> list[dict[str, Any]]:
    """
    Call Claude API with a natural language trip prompt.
    Returns a list of leg dicts matching the ItineraryLeg schema.
    Raises ValueError if the response cannot be parsed as valid leg JSON.
    """
    if MOCK:
        return _mock_response(prompt)
    return _real_call(prompt)


def _real_call(prompt: str) -> list[dict[str, Any]]:
    if not CLAUDE_API_KEY:
        raise RuntimeError("CLAUDE_API_KEY is not set in .env")

    headers = {
        "x-api-key":         CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type":      "application/json",
    }
    body = {
        "model":      CLAUDE_MODEL,
        "max_tokens": 1024,
        "system":     SYSTEM_PROMPT,
        "messages":   [{"role": "user", "content": prompt}],
    }

    response = httpx.post(CLAUDE_API_URL, headers=headers, json=body, timeout=30.0)
    response.raise_for_status()

    data = response.json()
    raw  = data["content"][0]["text"].strip()

    try:
        legs = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Claude returned invalid JSON: {e}\nRaw response: {raw}")

    if not isinstance(legs, list):
        raise ValueError(f"Claude response is not a JSON array. Got: {type(legs)}")

    return legs


def _mock_response(prompt: str) -> list[dict[str, Any]]:
    """
    Returns a realistic 3-leg mock itinerary for development.
    Used when CLAUDE_MOCK=true in .env.
    """
    return [
        {
            "order":                1,
            "origin_iata":         "DXB",
            "destination_iata":    "LHR",
            "depart_date":         "2026-08-01",
            "cabin_class":         "ECONOMY",
            "estimated_price_usd": 420,
            "duration_min":        435,
        },
        {
            "order":                2,
            "origin_iata":         "LHR",
            "destination_iata":    "CDG",
            "depart_date":         "2026-08-05",
            "cabin_class":         "ECONOMY",
            "estimated_price_usd": 110,
            "duration_min":        80,
        },
        {
            "order":                3,
            "origin_iata":         "CDG",
            "destination_iata":    "DXB",
            "depart_date":         "2026-08-10",
            "cabin_class":         "ECONOMY",
            "estimated_price_usd": 430,
            "duration_min":        420,
        },
    ]