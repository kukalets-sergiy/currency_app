import csv
from datetime import datetime, timedelta
from typing import Any

from django.db.models import Max, QuerySet
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from drf_yasg.inspectors import SwaggerAutoSchema
from rest_framework.pagination import PageNumberPagination

from .constants import CURRENCY_CODES
from .serializers import (
    CurrencyRateSerializer,
    AvailableCurrencySerializer,
    CurrencyCreateSerializer,
    CurrencyRateHistorySerializer,
    CurrencyHistoryQuerySerializer,
    CURRENCY_NAME_CHOICES,
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework import generics
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Currency, CurrencyRate
from django.utils import timezone


class CurrencySchema(SwaggerAutoSchema):
    def get_tags(self, operation_keys: list[str] | None = None) -> list[str]:
        return ["Currency Management"]


class CurrencyListView(generics.ListAPIView):
    swagger_schema = CurrencySchema
    serializer_class = CurrencyRateSerializer

    def get_queryset(self) -> QuerySet[CurrencyRate]:
        latest_ids = (
            CurrencyRate.objects.filter(currency__is_active=True)
            .values("currency")
            .annotate(last_id=Max("id"))
            .values_list("last_id", flat=True)
        )

        return CurrencyRate.objects.filter(id__in=latest_ids).select_related("currency")


class AvailableCurrencyListView(generics.ListAPIView):
    swagger_schema = CurrencySchema
    serializer_class = AvailableCurrencySerializer

    def get_queryset(self) -> list[dict[str, str]]:
        active_codes = set(
            Currency.objects.filter(is_active=True).values_list("code", flat=True)
        )

        available = [
            {"code": code, "name": name}
            for code, name in CURRENCY_CODES.items()
            if code not in active_codes
        ]

        return available


class CurrencyCreateView(generics.CreateAPIView):
    swagger_schema = CurrencySchema
    queryset = Currency.objects.all()
    serializer_class = CurrencyCreateSerializer
    parser_classes = [FormParser, MultiPartParser]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "code",
                openapi.IN_FORM,
                description="Select currency",
                type=openapi.TYPE_STRING,
                enum=[name for name, _ in CURRENCY_NAME_CHOICES],
                required=True,
            ),
        ],
        responses={201: CurrencyCreateSerializer},
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().post(request, *args, **kwargs)


class CurrencyHistoryPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = "page_size"
    max_page_size = 100


class CurrencyHistoryView(generics.ListAPIView):
    swagger_schema = CurrencySchema
    serializer_class = CurrencyRateHistorySerializer
    pagination_class = CurrencyHistoryPagination

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "start",
                openapi.IN_QUERY,
                description="Start date YYYY-MM-DD",
                default="2026-01-01",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
            ),
            openapi.Parameter(
                "end",
                openapi.IN_QUERY,
                description="End date YYYY-MM-DD",
                default="2027-01-01",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
            ),
            openapi.Parameter(
                "code",
                openapi.IN_PATH,
                description="Select currency",
                type=openapi.TYPE_STRING,
                enum=[name for name, _ in CURRENCY_NAME_CHOICES],
            ),
        ],
        responses={200: CurrencyRateHistorySerializer(many=True)},
    )
    def get(self, request: Request, code: str) -> Response:
        return super().get(request, code=code)

    def get_queryset(self) -> QuerySet[CurrencyRate]:
        code_param = self.kwargs["code"]

        from .serializers import CURRENCY_NAME_TO_CODE

        if isinstance(code_param, str) and code_param in CURRENCY_NAME_TO_CODE:
            code = CURRENCY_NAME_TO_CODE[code_param]
        else:
            try:
                code = int(code_param)
            except (ValueError, TypeError):
                from rest_framework.exceptions import ValidationError

                raise ValidationError(f"Invalid currency code: {code_param}")

        currency = get_object_or_404(Currency, code=code)

        query_serializer = CurrencyHistoryQuerySerializer(
            data=self.request.query_params
        )
        query_serializer.is_valid(raise_exception=True)

        validated = query_serializer.validated_data
        start: datetime = validated.get("start", timezone.now() - timedelta(days=30))
        end: datetime = validated.get("end", timezone.now())

        return (
            CurrencyRate.objects.filter(
                currency=currency,
                created_at__range=(start, end),
            )
            .select_related("currency")
            .order_by("created_at")
        )


class CurrencyToggleView(APIView):
    swagger_schema = CurrencySchema
    """ Enable/disable currency monitoring PATCH /currencies/<code>/toggle/ """

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "code",
                openapi.IN_PATH,
                description="Select currency",
                required=True,
                type=openapi.TYPE_STRING,
                enum=[name for name, _ in CURRENCY_NAME_CHOICES],
            ),
        ]
    )
    def patch(self, request: Request, code: str) -> Response:
        from .serializers import CURRENCY_NAME_TO_CODE

        if code in CURRENCY_NAME_TO_CODE:
            code_int = CURRENCY_NAME_TO_CODE[code]
        else:
            try:
                code_int = int(code)
            except (ValueError, TypeError):
                from rest_framework.exceptions import ValidationError

                raise ValidationError(f"Invalid currency code: {code}")

        currency = get_object_or_404(Currency, code=code_int)
        currency.is_active = not currency.is_active
        currency.save(update_fields=["is_active"])
        return Response({"code": currency.code, "is_active": currency.is_active})


class CurrencyRatesCSVView(APIView):
    swagger_schema = CurrencySchema

    def get(self, request: Request) -> HttpResponse:
        now = timezone.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"currency_rates_{now}.csv"

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        writer.writerow(["Currency", "Buy", "Sell", "Cross", "Date"])

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

        for r in rates:
            rate_buy = r.rate_buy or ""
            rate_sell = r.rate_sell or ""
            writer.writerow(
                [r.currency.name, rate_buy, rate_sell, r.rate_cross, r.created_at]
            )

        return response
