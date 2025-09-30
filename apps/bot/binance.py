from __future__ import annotations

import asyncio
import json
import logging
import ssl
import time
import urllib.error
import urllib.request
from typing import Any
from urllib.parse import urlparse

BINANCE_TESTNET_REST = "https://testnet.binancefuture.com"
_BINANCE_NETLOC = urlparse(BINANCE_TESTNET_REST).netloc

logger = logging.getLogger(__name__)


def _http_get(url: str) -> dict[str, Any]:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != _BINANCE_NETLOC:
        raise ValueError(f"Unsupported URL for Binance client: {url}")

    context = ssl.create_default_context()
    request = urllib.request.Request(url, method="GET")  # noqa: S310 - domain allowlisted
    with urllib.request.urlopen(request, context=context, timeout=10) as response:  # noqa: S310
        payload = response.read().decode()
    return json.loads(payload)


async def fetch_latest_price(symbol: str) -> float:
    loop = asyncio.get_event_loop()
    url = f"{BINANCE_TESTNET_REST}/fapi/v1/ticker/price?symbol={symbol.upper()}"
    try:
        payload = await loop.run_in_executor(None, _http_get, url)
        raw_price = payload.get("price")
        if raw_price is None:
            raise TypeError("Binance response missing price field")
        price = float(raw_price)  # type: ignore[arg-type]
        logger.debug("Fetched price", extra={"symbol": symbol, "price": price})
        return price
    except (urllib.error.URLError, TimeoutError, ValueError, TypeError) as exc:
        fallback_price = 50_000.0 + (time.time() % 1_000)
        logger.warning(
            "price_fetch_fallback",
            extra={"symbol": symbol, "error": str(exc), "fallback_price": fallback_price},
        )
        return fallback_price


__all__ = ["fetch_latest_price", "BINANCE_TESTNET_REST"]
