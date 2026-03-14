from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):

    # image_url = serializers.SerializerMethodField()
    # product_image = serializers.ReadOnlyField(source='product.image')

    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'quantity', 'price','image']

    # def get_imgUrl(self, obj):
    #     if obj.image:
    #         return obj.image.url 
    #     return "https://via.placeholder.com/150"

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True) # Related name 'items' 

    class Meta:
        model = Order
        fields = ['id', 'total_amount', 'is_paid', 'address', 'created_at', 'items','status']