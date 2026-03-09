from typing import Any
from django.db.models import Max, QuerySet
from django.core.management.base import BaseCommand
import csv
from currency_app.models import CurrencyRate
from django.utils import timezone


class Command(BaseCommand):
    help = "Export latest currency rates to CSV"

    def handle(self, *args: Any, **options: Any) -> None:
        now = timezone.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"currency_rates_{now}.csv"

        latest_ids = (
            CurrencyRate.objects.filter(currency__is_active=True)
            .values("currency")
            .annotate(latest_id=Max("id"))
            .values_list("latest_id", flat=True)
        )

        rates: QuerySet[CurrencyRate] = (
            CurrencyRate.objects.filter(id__in=latest_ids)
            .select_related("currency")
            .order_by("currency__code")
        )

        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Currency", "Buy", "Sell", "Cross", "Date"])

            for r in rates:
                rate_buy = r.rate_buy if r.rate_buy is not None else ""
                rate_sell = r.rate_sell if r.rate_sell is not None else ""
                writer.writerow(
                    [r.currency.name, rate_buy, rate_sell, r.rate_cross, r.created_at]
                )

        self.stdout.write(self.style.SUCCESS(f"CSV saved: {filename}"))
