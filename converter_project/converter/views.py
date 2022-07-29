import time
from typing import Any, Dict

from django.shortcuts import render
from django.views.generic import TemplateView

from .models import Currency, PaymentMethod
from .utils.json_parser import parse_payment_methods

# Create your views here.

PATHS = {
    'RUB': '/home/shark1501/dev/p2p_converter/converter_project/test_data/10_records_RUB_mixed.json',
    'TRY': '/home/shark1501/dev/p2p_converter/converter_project/test_data/10_records_TRY_mixed.json',
}


def index(request):
    template = 'converter/index.html'
    if request.method == 'GET':
        context = {
            'currencies': Currency.objects.all(),
        }
        return render(request, template, context)

    if request.method == 'POST':
        context = {
            'currencies': Currency.objects.all(),
            'POST': request.POST,
        }
        return render(request, template, context)


def get_payment_methods(request):
    context = {}
    if request.GET.get('sell_currency'):
        currency_id_to_parse = request.GET.get('sell_currency')
        context['payment_method_type'] = 'SELL'
        time.sleep(0.1)
    elif request.GET.get('buy_currency'):
        currency_id_to_parse = request.GET.get('buy_currency')
        context['payment_method_type'] = 'BUY'
        # to address SQlite limitation on concurrent requests
        time.sleep(0.2)
    currency: Currency = Currency.objects.get(pk=currency_id_to_parse)
    parse_payment_methods(PATHS[currency.code])
    payment_methods = PaymentMethod.objects.filter(
        currency=currency)

    context['payment_methods'] = payment_methods
    return render(request,
                  'converter/includes/payment_methods_dropdown.html',
                  context)
