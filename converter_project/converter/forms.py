"""Currency converter forms."""
from django import forms
from django.db.models.query import QuerySet
from dynamic_forms import DynamicField, DynamicFormMixin

from .models import Currency, PaymentMethod


class ConverterForm(DynamicFormMixin, forms.Form):
    """Currency converter form."""

    def get_sell_payment_methods(form: 'ConverterForm'
                                 ) -> QuerySet[PaymentMethod]:
        """Get queryset of payment methods for selected currency.

        Will be used as callable with form argument by DynamicField field,
        as queryset source.
        """
        sell_currency = form['sell_currency'].value()
        return PaymentMethod.objects.filter(currency=sell_currency)

    def get_buy_payment_methods(form: 'ConverterForm'
                                ) -> QuerySet[PaymentMethod]:
        """Get queryset of payment methods for selected currency.

        Will be used as callable with form argument by DynamicField field,
        as queryset source.
        """
        buy_currency = form['buy_currency'].value()
        return PaymentMethod.objects.filter(currency=buy_currency)

    def initial_sell_payment_method(form: 'ConverterForm'
                                    ) -> PaymentMethod:
        """Get first payment method for selected currency.

        Will be used as callable with form argument by DynamicField field,
        as initial field value source.
        """
        sell_currency = form['sell_currency'].value()
        return PaymentMethod.objects.filter(currency=sell_currency).first()

    def initial_buy_payment_method(form: 'ConverterForm'
                                   ) -> PaymentMethod:
        """Get first payment method for selected currency.

        Will be used as callable with form argument by DynamicField field,
        as initial field value source.
        """
        buy_currency = form['buy_currency'].value()
        return PaymentMethod.objects.filter(currency=buy_currency).first()

    sell_currency = forms.ModelChoiceField(
        queryset=Currency.objects.all()
    )
    buy_currency = forms.ModelChoiceField(
        queryset=Currency.objects.all()
    )
    sell_payment_methods = DynamicField(
        forms.ModelChoiceField,
        queryset=get_sell_payment_methods,
        initial=initial_sell_payment_method,
        error_messages={
            'invalid_choice': "Payment methods for selected currency doesn't exist"
        }
    )
    buy_payment_methods = DynamicField(
        forms.ModelChoiceField,
        queryset=get_buy_payment_methods,
        initial=initial_buy_payment_method,
        error_messages={
            'invalid_choice': "Payment methods for selected currency doesn't exist"
        }
    )
