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

    def get_from_payment_methods(form: 'ConverterForm'
                                 ) -> QuerySet[PaymentMethod]:
        """Get queryset of payment methods for selected currency.

        Will be used as callable with form argument by DynamicField field,
        as queryset source.
        """
        from_currency = form['from_currency'].value()
        return PaymentMethod.objects.filter(currency=from_currency)

    def get_to_payment_methods(form: 'ConverterForm'
                               ) -> QuerySet[PaymentMethod]:
        """Get queryset of payment methods for selected currency.

        Will be used as callable with form argument by DynamicField field,
        as queryset source.
        """
        to_currency = form['to_currency'].value()
        return PaymentMethod.objects.filter(currency=to_currency)

    def initial_from_payment_method(form: 'ConverterForm'
                                    ) -> PaymentMethod:
        """Get first payment method for selected currency.

        Will be used as callable with form argument by DynamicField field,
        as initial field value source.
        """
        from_currency = form['from_currency'].value()
        return PaymentMethod.objects.filter(currency=from_currency).first()

    def initial_to_payment_method(form: 'ConverterForm'
                                  ) -> PaymentMethod:
        """Get first payment method for selected currency.

        Will be used as callable with form argument by DynamicField field,
        as initial field value source.
        """
        to_currency = form['to_currency'].value()
        return PaymentMethod.objects.filter(currency=to_currency).first()

    from_currency = forms.ModelChoiceField(
        queryset=Currency.objects.all()
    )
    to_currency = forms.ModelChoiceField(
        queryset=Currency.objects.all()
    )
    from_payment_methods = DynamicField(
        forms.ModelChoiceField,
        queryset=get_from_payment_methods,
        initial=initial_from_payment_method,
        error_messages={
            'invalid_choice': ERROR_MESSAGE,
        }
    )
    to_payment_methods = DynamicField(
        forms.ModelChoiceField,
        queryset=get_to_payment_methods,
        initial=initial_to_payment_method,
        error_messages={
            'invalid_choice': ERROR_MESSAGE,
        }
    )
    from_amount = forms.FloatField(required=False)
    to_amount = forms.FloatField()

    is_merchant = forms.BooleanField(required=False, initial=True)
    # TODO Handle same currency selected ib both dropbowns. Should throw error
    # TODO install debug toolbar
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
