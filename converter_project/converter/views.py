from django.http import HttpResponse
from django.shortcuts import render

from .forms import ConverterForm

# Create your views here.

PATHS = {
    'RUB': '/home/shark1501/dev/p2p_converter/converter_project/test_data/10_records_RUB_mixed.json',
    'TRY': '/home/shark1501/dev/p2p_converter/converter_project/test_data/10_records_TRY_mixed.json',
}


def index(request) -> HttpResponse:
    """Handle requests to main converter page."""
    template = 'converter/index.html'
    form = ConverterForm()
    context = {
        'form': form,
    }
    if request.method == 'POST':
        form = ConverterForm(request.POST)
        context = {
            'form': form,
            'POST': request.POST,
        }
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
    for currency, payment_method in currency_payment_method.items():
        if currency in request.GET.keys():
            return HttpResponse(form[payment_method])
