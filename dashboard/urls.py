from django.urls import path
from .views import DashboarView,UserListUpdateView,ProductAdminAPIView,AdminOrdersView

urlpatterns =[
  path('admin-dashboard/',DashboarView.as_view()),
  path('users/', UserListUpdateView.as_view(), name='user-list'),
  path('users/<int:pk>/', UserListUpdateView.as_view(), name='user-update'),
  path('admin-products/',ProductAdminAPIView.as_view()),
  path('admin-products/<int:pk>/',ProductAdminAPIView.as_view()),
  path('admin-orders/',AdminOrdersView.as_view()),
  path('admin-orders/<int:pk>/',AdminOrdersView.as_view()),


]