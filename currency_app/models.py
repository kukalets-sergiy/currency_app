from django.core.validators import MinValueValidator
from django.db import models


class Currency(models.Model):
    code = models.IntegerField(unique=True)
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


class CurrencyRate(models.Model):
    currency = models.ForeignKey(
        Currency, on_delete=models.CASCADE, related_name="rates"
    )
    name = models.CharField(max_length=50, blank=True)
    rate_buy = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    rate_sell = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    rate_cross = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(
                fields=["currency", "-created_at"], name="curr_rate_curr_date_idx"
            ),
            models.Index(fields=["-created_at"], name="curr_rate_date_idx"),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.currency.name} - Buy: {self.rate_buy}, Sell: {self.rate_sell} at {self.created_at}"
