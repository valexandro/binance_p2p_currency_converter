"""Currency converter forms."""
from django import forms
from dynamic_forms import DynamicField, DynamicFormMixin

from .models import Currency, PaymentMethod

# TODO Add warning if no payment methods found


class ConverterForm(DynamicFormMixin, forms.Form):
    """Currency converter form."""

    def get_sell_payment_methods(form):
        """Get queryset of payment methods for selected currency."""
        sell_currency = form['sell_currency'].value()
        return PaymentMethod.objects.filter(currency=sell_currency)

    def get_buy_payment_methods(form):
        """Get queryset of payment methods for selected currency."""
        buy_currency = form['buy_currency'].value()
        return PaymentMethod.objects.filter(currency=buy_currency)

    def initial_sell_payment_method(form):
        """Get first payment method for selected currency."""
        sell_currency = form['sell_currency'].value()
        return PaymentMethod.objects.filter(currency=sell_currency).first()

    def initial_buy_payment_method(form):
        """Get first payment method for selected currency."""
        buy_currency = form['buy_currency'].value()
        return PaymentMethod.objects.filter(currency=buy_currency).first()

    sell_currency = forms.ModelChoiceField(
        queryset=Currency.objects.all())
    buy_currency = forms.ModelChoiceField(
        queryset=Currency.objects.all())

    sell_payment_methods = DynamicField(
        forms.ModelChoiceField,
        queryset=get_sell_payment_methods,
        initial=initial_sell_payment_method,
    )
    buy_payment_methods = DynamicField(
        forms.ModelChoiceField,
        queryset=get_buy_payment_methods,
        initial=initial_buy_payment_method,
    )
