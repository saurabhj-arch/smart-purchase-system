from django.urls import path
from .views import SearchView, ProductPriceView

urlpatterns = [
    path("", SearchView.as_view(), name="search"),
    path("product/<int:product_id>/", ProductPriceView.as_view(), name="product-prices"),
]