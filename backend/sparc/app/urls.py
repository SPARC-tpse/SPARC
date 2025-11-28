from django.urls import path
from .views import OrderListCreateView, OrderDetailView


urlpatterns = [
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path("orders/", OrderListCreateView.as_view(), name="order-list-create"),
]
