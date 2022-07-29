from locale import currency
from multiprocessing import context
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


class IndexView(TemplateView):
    template_name = 'converter/index.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['currencies'] = Currency.objects.all()
        return context


def get_payment_methods(request):
    sell_currency_id = request.GET.get('sell_currency')
    buy_currency_id = request.GET.get('buy_currency')
    if sell_currency_id and not buy_currency_id:
        sell_currency: Currency = Currency.objects.get(pk=sell_currency_id)
        parse_payment_methods(PATHS[sell_currency.code])
        sell_payment_methods = PaymentMethod.objects.filter(
            currency=sell_currency)
        context = {
            'sell_payment_methods': sell_payment_methods,
        }
        return render(request,
                      'converter/includes/sell_payment_methods_dropdown.html',
                      context)
    elif buy_currency_id and not sell_currency_id:
        buy_currency: Currency = Currency.objects.get(pk=buy_currency_id)
        parse_payment_methods(PATHS[buy_currency.code])
        buy_payment_methods = PaymentMethod.objects.filter(
            currency=buy_currency)
        context = {
            'buy_payment_methods': buy_payment_methods,
        }
        return render(request,
                      'converter/includes/buy_payment_methods_dropdown.html',
                      context)
