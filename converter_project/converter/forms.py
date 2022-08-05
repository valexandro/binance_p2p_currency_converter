"""Currency converter forms."""
from django import forms
from django.db.models.query import QuerySet
from dynamic_forms import DynamicField, DynamicFormMixin

from .models import Currency, PaymentMethod


class ConverterForm(DynamicFormMixin, forms.Form):
    """Currency converter form."""

    ERROR_MESSAGE = (
        'No payment methods for selected currency. '
        'Please select another currency.')

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
            'invalid_choice': ERROR_MESSAGE,
        }
    )
    buy_payment_methods = DynamicField(
        forms.ModelChoiceField,
        queryset=get_buy_payment_methods,
        initial=initial_buy_payment_method,
        error_messages={
            'invalid_choice': ERROR_MESSAGE,
        }
    )
    buy_amount = forms.FloatField(required=False)
    sell_amount = forms.FloatField(required=False)

    # TODO Implement sell and buy amount fields.
    # Either of them can be filled.
    # if only sell_amount filled -
    # 1. get offers for sell currency with selected amount and payment method,
    # 2. calculate amount of USDT to get
    # 3. get offers for buy currency with selected payment method, and empty amount, and calculate approximate
    # amount of buy currency to get (will be best price possible)
    # 4. get offers for buy currency with calculated amount and selected payment method
    # 5. finally use best offer from 1 and 4 to calculate conversion rate

    # if only buy_amount filled
    # 1. get offers for buy currency with selected amount payment method
    # 2. calculate amount of USDT needed
    # 3. get offers for sell currency with selected payment method, and empty amount, and calculate approximate
    # amount of sell currency needed
    # 4. get offers for sell currency with calculated amount and selected payment method
    # 5. finally use best offer from 1 and 4 to calculate conversion rate

    # if both filled
    # on attempt to fill one field if other has data in it, clear other field.
# https://stackoverflow.com/questions/69403137/clear-input-field-when-text-is-entered-into-another-input-field
    # buy_amount
    # sell_amount
