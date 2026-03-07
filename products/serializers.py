from rest_framework import serializers
from .models import Products, Cart, Wishlist

class ProductsSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = Products
        fields = '__all__' 

    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            # Default fallback for local development
            return f"http://127.0.0.1:8000{obj.image.url}"
        return None    


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