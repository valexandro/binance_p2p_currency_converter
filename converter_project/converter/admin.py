from django.contrib import admin

from .models import Currency, PaymentMethod


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'display_name', 'currency', 'date_updated',)


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('pk', 'code', 'name',)
