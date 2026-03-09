from rest_framework import serializers
from .models import Products, Cart, Wishlist

class ProductsSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = Products
        fields = '__all__' 

    

class CartSerializer(serializers.ModelSerializer):
    product = ProductsSerializer(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'product', 'quantity']

class WishlistSerializer(serializers.ModelSerializer):
    product = ProductsSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'product']