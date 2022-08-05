from django.http import HttpResponse
from django.shortcuts import render

from .utils.json_parser import parse_payment_methods
from .utils.binance_api import get_p2p_offers_data

from .forms import ConverterForm
from .models import Currency, PaymentMethod

# Create your views here.

PATHS = {
    'RUB': '/home/shark1501/dev/p2p_converter/converter_project/test_data/10_records_RUB_mixed.json',
    'TRY': '/home/shark1501/dev/p2p_converter/converter_project/test_data/10_records_TRY_mixed.json',
}


def index(request) -> HttpResponse:
    """Handle requests to main converter page."""
    template = 'converter/index.html'
    form = ConverterForm(request.POST or None)
    context = {
        'form': form,
    }
    if form.is_valid():
        context['POST'] = request.POST
    return render(request, template, context)


def get_payment_methods(request) -> HttpResponse:
    """Return payment method options for requested currency as HTML select options.

    Implemented by DynamicField in ConverterForm.
    Call to forms '*payment_methods' field for requested currency,
    will trigger forms method to fetch payment methods for this currency,
    and assign resulting queryset to choisefield queryset, that will be
    returned as HTML.
    """
    form = ConverterForm(request.GET)
    currency_payment_method = {
        'sell_currency': 'sell_payment_methods',
        'buy_currency': 'buy_payment_methods',
    }
    for currency_type, payment_method in currency_payment_method.items():
        if currency_type in request.GET.keys():
            currency = Currency.objects.get(pk=request.GET.get(currency_type))
            # json = PATHS[currency.code]
            # parse_payment_methods(json)
            json = get_p2p_offers_data(currency.code)
            parse_payment_methods(json)
            payment_methods = PaymentMethod.objects.filter(currency=currency)
            if not payment_methods:
                return HttpResponse(
                    f'<option>Payment methods for {currency.code} not exists.</option>')
            return HttpResponse(form[payment_method])
