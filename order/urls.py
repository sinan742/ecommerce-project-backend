from django.urls import path
from .views import PlaceOrderCODView

urlpatterns = [
    path('place-order-cod/', PlaceOrderCODView.as_view(), name='place-order-cod'),
]