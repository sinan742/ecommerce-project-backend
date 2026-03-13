from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Products, Cart, Wishlist
from .serializers import ProductsSerializer, CartSerializer, WishlistSerializer
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import RetrieveAPIView
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination

# --- PRODUCTS API ---
class ProductsApiview(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        products = Products.objects.all()
        serializer = ProductsSerializer(products, many=True)
        return Response(serializer.data)

class ProductDetailApiview(RetrieveAPIView):

    permission_classes = [AllowAny]
    queryset = Products.objects.all()
    serializer_class = ProductsSerializer


class CartPagination(PageNumberPagination): # pagination class
    page_size = 3

# --- CART API ---
class CartView(APIView):
    permission_classes = [IsAuthenticated] 

    def get(self, request):
        cart_items = Cart.objects.filter(user=request.user).order_by('-id')
        
        # English: Check if the frontend wants all items (for Checkout)
        show_all = request.query_params.get('all') == 'true'

        if show_all:
            # English: Return everything without pagination
            serializer = CartSerializer(cart_items, many=True)
            return Response(serializer.data)
        
        paginator = CartPagination()
        page = paginator.paginate_queryset(cart_items, request)
        serializer = CartSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):

        product_id = request.data.get('product_id') or request.data.get('product')
        if not product_id:
            return Response({"error": "Product ID is required"}, status=400)

        product = get_object_or_404(Products, id=product_id)
        
        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
        if not created:
            cart_item.quantity += 1
            cart_item.save()
            
        return Response({"message": "Added to Bag"}, status=status.HTTP_201_CREATED)
    
    def put(self, request, pk=None):
        try:
            # English: Get the specific cart item using the ID from URL
            cart_item = Cart.objects.get(id=pk, user=request.user)
            
            # English: Get new quantity from request body
            new_quantity = request.data.get('quantity')
            
            if new_quantity and int(new_quantity) > 0:
                cart_item.quantity = new_quantity
                cart_item.save()
                return Response({"message": "Quantity updated"}, status=200)
            
            return Response({"error": "Invalid quantity"}, status=400)
            
        except Cart.DoesNotExist:
            return Response({"error": "Item not found"}, status=404)

    def delete(self, request, pk):
        item = get_object_or_404(Cart, id=pk, user=request.user)
        item.delete()
        return Response({"message": "Removed from cart"}, status=status.HTTP_204_NO_CONTENT)

# --- WISHLIST API ---
class WishlistView(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = Wishlist.objects.filter(user=request.user)
        serializer = WishlistSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        product_id = request.data.get('product_id') or request.data.get('product')
        product = get_object_or_404(Products, id=product_id)
        Wishlist.objects.get_or_create(user=request.user, product=product)
        return Response({"message": "Added to wishlist"}, status=201)

    def delete(self, request, pk):
        item = get_object_or_404(Wishlist, id=pk, user=request.user)
        item.delete()
        return Response({"message": "Removed from wishlist"}, status=204)

