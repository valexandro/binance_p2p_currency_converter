from django.urls import path

from . import views


urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('payment_methods/', views.get_payment_methods, name='payment_methods')
]
