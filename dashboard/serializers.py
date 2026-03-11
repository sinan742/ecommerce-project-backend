from rest_framework import serializers
from django.contrib.auth.models import User
from products.models import Products
from order.models import Order, OrderItem

class UserManagementSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'status']

    def get_status(self, obj):
        return "Active" if obj.is_active else "Blocked"

class ProductAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ['id', 'name', 'brand', 'price', 'stock', 'description', 'image']

class OrderItemSerializer(serializers.ModelSerializer):
    imgUrl = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'quantity', 'price', 'imgUrl']

    def get_imgUrl(self, obj):
        if obj.image:
            return obj.image
        return "https://via.placeholder.com/150" 

class OrderAdminSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user_name', 'total_amount', 'is_paid', 'address', 'status', 'created_at', 'items']