from django.urls import path
from .views import (
    CurrencyListView,
    AvailableCurrencyListView,
    CurrencyCreateView,
    CurrencyToggleView,
    CurrencyHistoryView,
    CurrencyRatesCSVView,
)

app_name = "currency_app"

urlpatterns = [
    path("currencies/", CurrencyListView.as_view(), name="currency-list"),
    path(
        "currencies/available/",
        AvailableCurrencyListView.as_view(),
        name="currency-available",
    ),
    path("currencies/add/", CurrencyCreateView.as_view(), name="currency-add"),
    path(
        "currencies/<str:code>/history/",
        CurrencyHistoryView.as_view(),
        name="currency-history",
    ),
    path(
        "currencies/<str:code>/toggle/",
        CurrencyToggleView.as_view(),
        name="currency-toggle",
    ),
    path(
        "currencies/export/csv/",
        CurrencyRatesCSVView.as_view(),
        name="currency-export-csv",
    ),
]
