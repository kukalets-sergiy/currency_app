from typing import Any

from celery import shared_task
from django.db.models import QuerySet

from .constants import UAH_CODE, MAX_RECORDS_PER_CURRENCY
from .models import Currency, CurrencyRate
from django.db import transaction

from .services import fetch_monobank_currency

import logging

logger = logging.getLogger(__name__)


@shared_task
def get_currency_rates() -> None:
    data: list[dict[str, Any]] = fetch_monobank_currency()
    if not data:
        return

    rate_map: dict[int, dict[str, Any]] = {
        item["currencyCodeA"]: item
        for item in data
        if item.get("currencyCodeB") == UAH_CODE
    }

    active_currencies: QuerySet[Currency] = Currency.objects.filter(is_active=True)

    with transaction.atomic():
        for currency in active_currencies:
            rate_info = rate_map.get(currency.code)
            if not rate_info:
                continue

            rate_obj = CurrencyRate.objects.create(
                currency=currency,
                name=currency.name,
                rate_buy=rate_info.get("rateBuy"),
                rate_sell=rate_info.get("rateSell"),
                rate_cross=rate_info.get("rateCross"),
            )

            if rate_obj.name != currency.name:
                rate_obj.name = currency.name
                rate_obj.save(update_fields=["name"])

            keep_ids = (
                CurrencyRate.objects.filter(currency=currency)
                .order_by("-created_at")
                .values_list("id", flat=True)[:MAX_RECORDS_PER_CURRENCY]
            )

            deleted_count, _ = (
                CurrencyRate.objects.filter(currency=currency)
                .exclude(id__in=keep_ids)
                .delete()
            )

            if deleted_count > 0:
                logger.debug(f"Deleted {deleted_count} old rates for {currency.name}")

    logger.info(
        f"Updated currency rates for {active_currencies.count()} active currencies."
    )
