from django.contrib import admin
from .models import Currency, CurrencyRate


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active", "created_at", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name", "code")
    ordering = ("code",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(CurrencyRate)
class CurrencyRateAdmin(admin.ModelAdmin):
    list_display = ("currency", "rate_buy", "rate_sell", "rate_cross", "created_at")
    list_filter = ("currency__is_active",)
    search_fields = ("currency__code", "currency__name")
    ordering = ("-created_at",)
    readonly_fields = ("currency", "rate_buy", "rate_sell", "rate_cross", "created_at")
