from langchain_core.tools import tool
from datetime import datetime
import httpx
import pytz
import math
import re


@tool
def get_current_time(timezone: str = "Asia/Kolkata") -> str:
    """Returns current date and time for a given timezone like Asia/Kolkata or America/New_York."""
    try:
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        return f"Current date and time in {timezone}: {now.strftime('%A, %d %B %Y %I:%M %p')}"
    except Exception:
        return f"Current date and time: {datetime.now().strftime('%A, %d %B %Y %I:%M %p')}"


@tool
def calculate(expression: str) -> str:
    """Evaluates math expressions. Examples: 2+2, sqrt(144), 15% of 50000, 2**10"""
    try:
        if "% of" in expression.lower():
            parts = expression.lower().split("% of")
            expression = f"{parts[0].strip()} / 100 * {parts[1].strip()}"
        safe_dict = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
        result = eval(expression, {"__builtins__": {}}, safe_dict)
        return f"Result: {result:,}" if isinstance(result, (int, float)) else f"Result: {result}"
    except Exception as e:
        return f"Could not calculate: {str(e)}"


@tool
def get_weather(city: str) -> str:
    """Gets current weather for any city like Mumbai, Delhi, London, New York."""
    try:
        response = httpx.get(f"https://wttr.in/{city}?format=j1", timeout=10)
        data = response.json()
        current = data["current_condition"][0]
        area = data["nearest_area"][0]
        city_name = area["areaName"][0]["value"]
        country = area["country"][0]["value"]
        return (
            f"Weather in {city_name}, {country}:\n"
            f"Temperature: {current['temp_C']}C (feels like {current['FeelsLikeC']}C)\n"
            f"Condition: {current['weatherDesc'][0]['value']}\n"
            f"Humidity: {current['humidity']}%\n"
            f"Wind: {current['windspeedKmph']} km/h"
        )
    except Exception:
        return f"Could not fetch weather for {city}."


@tool
def convert_currency(amount_and_currencies: str) -> str:
    """Converts currency. Format: 100 USD to INR or 50 EUR to GBP."""
    try:
        parts = amount_and_currencies.lower().split()
        amount = float(parts[0])
        from_cur = parts[1].upper()
        to_cur = parts[3].upper()
        data = httpx.get(f"https://api.exchangerate-api.com/v4/latest/{from_cur}", timeout=10).json()
        rate = data["rates"][to_cur]
        return f"{amount:,.2f} {from_cur} = {amount * rate:,.2f} {to_cur}\n(Rate: 1 {from_cur} = {rate:.4f} {to_cur})"
    except Exception:
        return "Could not convert currency. Use format: 100 USD to INR"


@tool
def fetch_url(url: str) -> str:
    """Fetches and reads content from any URL, website, LinkedIn profile, GitHub repo, or any link."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        }
        response = httpx.get(url, headers=headers, timeout=15, follow_redirects=True)
        text = response.text
        text = re.sub(r'<script[^>]*>[\s\S]*?</script>', '', text)
        text = re.sub(r'<style[^>]*>[\s\S]*?</style>', '', text)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:3000] + "..." if len(text) > 3000 else text
    except Exception as e:
        return f"Could not fetch URL: {str(e)}"