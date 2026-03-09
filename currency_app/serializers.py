from typing import Any
from rest_framework import serializers

from .constants import CURRENCY_CODES
from .models import Currency, CurrencyRate


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ["id", "code", "name", "is_active", "created_at", "updated_at"]


CURRENCY_NAME_TO_CODE: dict[str, int] = {v: k for k, v in CURRENCY_CODES.items()}
CURRENCY_NAME_CHOICES: list[tuple[str, str]] = [
    (v, f"{v} ({k})") for k, v in CURRENCY_CODES.items()
]


class AvailableCurrencySerializer(serializers.Serializer):
    name = serializers.CharField()
    code = serializers.IntegerField()


class CurrencyCodeField(serializers.IntegerField):
    """Custom field that displays currency names in Swagger but processes codes"""

    def to_internal_value(self, data):
        if isinstance(data, str) and data in CURRENCY_NAME_TO_CODE:
            return CURRENCY_NAME_TO_CODE[data]
        if isinstance(data, (int, str)):
            try:
                code = int(data)
                if code in CURRENCY_CODES:
                    return code
            except (ValueError, TypeError):
                pass
        raise serializers.ValidationError(f"Invalid currency: {data}")

    def to_representation(self, value):
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
        return value


class CurrencyCreateSerializer(serializers.ModelSerializer):
    code = CurrencyCodeField(help_text="Select currency")

    class Meta:
        model = Currency
        fields = ["code", "name"]
        read_only_fields = ["name"]

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        code = attrs.get("code")
        if code is None:
            raise serializers.ValidationError("Code is required.")

        if code not in CURRENCY_CODES:
            raise serializers.ValidationError("Invalid currency code.")

        return attrs

    def create(self, validated_data: dict[str, Any]) -> Currency:
        code = validated_data["code"]
        name = CURRENCY_CODES.get(code)
        obj, created = Currency.objects.get_or_create(
            code=code, defaults={"name": name}
        )
        if not created:
            raise serializers.ValidationError("Currency with this code already exists.")
        return obj


class CurrencyRateSerializer(serializers.ModelSerializer):
    currency = CurrencySerializer()

    class Meta:
        model = CurrencyRate
        fields = ["currency", "rate_buy", "rate_sell", "rate_cross", "created_at"]


class CurrencyRateHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyRate
        fields = ["created_at", "rate_buy", "rate_sell", "rate_cross"]


class CurrencyHistoryQuerySerializer(serializers.Serializer):
    start = serializers.DateTimeField(required=False)
    end = serializers.DateTimeField(required=False)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        start = attrs.get("start")
        end = attrs.get("end")

        if start and end and start > end:
            raise serializers.ValidationError(
                {"end": "End datetime must be greater than or equal to start datetime."}
            )

        return attrs
