from django.urls import path
from .views import ProductsApiview,CartView,WishlistView,ProductDetailApiview
urlpatterns=[
    path('products/',ProductsApiview.as_view()),
    path('products/<int:pk>/', ProductDetailApiview.as_view()),
    path('cart/',CartView.as_view()),
    path('cart/<int:pk>/',CartView.as_view()),
    path('wishlist/',WishlistView.as_view()),
    path('wishlist/<int:pk>/',WishlistView.as_view()),

]