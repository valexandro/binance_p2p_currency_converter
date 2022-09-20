"""Currency converter forms."""
import logging

from django import forms
from django.core.exceptions import ValidationError
from dynamic_forms import DynamicField, DynamicFormMixin

from .models import Currency, PaymentMethod

logger = logging.getLogger(__name__)


class ConverterForm(DynamicFormMixin, forms.Form):
    """Currency converter form."""

    from_currency = forms.ModelChoiceField(
        queryset=Currency.objects.all()
    )
    to_currency = forms.ModelChoiceField(
        queryset=Currency.objects.all()
    )
    from_payment_methods = DynamicField(
        forms.ModelChoiceField,
        queryset=lambda form: PaymentMethod.objects.filter(
            currency=form['from_currency'].value()),
        initial=lambda form: PaymentMethod.objects.filter(
            currency=form['from_currency'].value()).first(),
    )
    to_payment_methods = DynamicField(
        forms.ModelChoiceField,
        queryset=lambda form: PaymentMethod.objects.filter(
            currency=form['to_currency'].value()),
        initial=lambda form: PaymentMethod.objects.filter(
            currency=form['to_currency'].value()).first(),
    )
    from_amount = forms.FloatField(required=False)
    to_amount = forms.FloatField(required=False)

    is_merchant = forms.BooleanField(required=False, initial=True)

    def clean(self):
        cleaned_data = super().clean()
        from_amount = cleaned_data.get('from_amount')
        to_amount = cleaned_data.get('to_amount')
        from_currency = cleaned_data.get('from_currency')
        to_currency = cleaned_data.get('to_currency')

        if not from_amount and not to_amount:
            raise ValidationError('Please fill one of amount fields!')

        if from_amount and to_amount:
            raise ValidationError('Please fill only one amount field!')

        if from_currency == to_currency:
            raise ValidationError('From and to currencies cannot be the same!')

        if from_amount and from_amount <= 0 or to_amount and to_amount <= 0:
            raise ValidationError('Amount should be greater than zero!')
