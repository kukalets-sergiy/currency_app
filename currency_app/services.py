import logging
import requests
from typing import Any

from django.core.cache import cache

MONOBANK_API_URL = "https://api.monobank.ua/bank/currency"
CACHE_KEY = "monobank_currency"
CACHE_TTL = 60
API_TIMEOUT = 10

logger = logging.getLogger(__name__)


def fetch_monobank_currency() -> list[dict[str, Any]]:
    """
    Gets currency rates from Monobank API with caching.

    Returns:
        list[dict[str, Any]]: List of currency rates

    Raises:
        requests.RequestException: When an API request error
        ValueError: On JSON parsing error
    """
    cached: list[dict[str, Any]] | None = cache.get(CACHE_KEY)

    if cached:
        logger.debug("Returning cached currency rates")
        return cached

    try:
        logger.info(f"Fetching currency rates from {MONOBANK_API_URL}")
        res = requests.get(MONOBANK_API_URL, timeout=API_TIMEOUT)
        res.raise_for_status()

        data: list[dict[str, Any]] = res.json()

        if not isinstance(data, list):
            raise ValueError("Invalid response format from Monobank API")

        cache.set(CACHE_KEY, data, CACHE_TTL)
        logger.info(f"Successfully cached {len(data)} currency rates")

        return data

    except requests.RequestException as e:
        logger.error(f"Failed to fetch currency rates from Monobank: {e}")
        raise
    except ValueError as e:
        logger.error(f"Failed to parse JSON response from Monobank: {e}")
        raise
