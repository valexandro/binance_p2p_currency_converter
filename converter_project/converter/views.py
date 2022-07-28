from locale import currency
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
        context['sell_currencies'] = Currency.objects.all()
        context['buy_currencies'] = Currency.objects.all()
        return context


def get_payment_methods(request):
    currency_id = request.GET.get('sell_currency')
    currency: Currency = Currency.objects.get(pk=currency_id)
    parse_payment_methods(PATHS[currency.code])
    payment_methods = PaymentMethod.objects.filter(currency=currency)
    return render(request, 'converter/includes/payment_methods.html', {'payment_methods': payment_methods})
