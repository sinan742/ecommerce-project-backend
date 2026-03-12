from django.shortcuts import render
from django.contrib.auth.models import User
from products.models import Products
from order.models import Order
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserManagementSerializer
from rest_framework import status
from products.models import Products
from .serializers import ProductAdminSerializer
from django.shortcuts import get_object_or_404
from products.models import Products  
from .serializers import ProductAdminSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from order.models import Order
from .serializers import OrderAdminSerializer
from django.db.models import Q
from django.db.models import Count
from django.db.models.functions import TruncDate
from order.models import Order


class DashboarView(APIView):
    permission_classes=[IsAdminUser]

    def get(self, request):
        
        graph_data = Order.objects.annotate(date=TruncDate('created_at')) \
                           .values('date') \
                           .annotate(orders=Count('id')) \
                           .order_by('date')[:7]

        return Response({
            "total_users": User.objects.count(),
            "total_products": Products.objects.count(),
            "total_orders": Order.objects.count(),
            "total_revenue": sum(o.total_amount for o in Order.objects.filter(is_paid=False)),
            "graph_data": [{"date": d['date'].strftime('%d %b'), "orders": d['orders']} for d in graph_data]
        })


# user managment view

class UserListUpdateView(APIView):
    
    permission_classes = [IsAdminUser] 

    def get(self, request):
        users = User.objects.all().exclude(is_superuser=True) 
        serializer = UserManagementSerializer(users, many=True)
        return Response(serializer.data)

    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            new_status = request.data.get('status')
            
            if new_status == "Active":
                user.is_active = True
            elif new_status == "Blocked":
                user.is_active = False
            
            user.save()
            serializer = UserManagementSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_SERVER_ERROR)

# ----PRODUCTS GET AND POST

class ProductAdminAPIView(APIView):

    permission_classes=[IsAdminUser]
    parser_classes=(MultiPartParser,FormParser)
    
    def get(self, request):

        search_query = request.query_params.get('search', None)

        products = Products.objects.all().order_by('-id')
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) | 
                Q(brand__icontains=search_query)
            )
        serializer = ProductAdminSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductAdminSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#---PRODUCTS PUT AND DELETE---

class ProductDetailAPIView(APIView):

    permission_classes =[IsAdminUser]
   
    parser_classes=(MultiPartParser,FormParser)

    def put(self, request, pk):
        product = get_object_or_404(Products, pk=pk)
        serializer = ProductAdminSerializer(product, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        product = get_object_or_404(Products, pk=pk)
        product.delete()
        return Response({"message": "Product deleted"}, status=status.HTTP_204_NO_CONTENT)

# ----Admin Orders---

class AdminOrdersView(APIView):
    # അഡ്മിൻ മാത്രമേ ഈ ഡാറ്റ കാണാവൂ എന്ന് ഉറപ്പാക്കുക

    def get(self, request):
        # പുതിയ ഓർഡറുകൾ ആദ്യം വരാൻ -id അല്ലെങ്കിൽ -created_at നൽകാം
        orders = Order.objects.all().order_by('-id')
        serializer = OrderAdminSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        serializer = OrderAdminSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save() # ഇവിടെ സിഗ്നൽ വർക്ക് ആവുകയും മെയിൽ പോവുകയും ചെയ്യും
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        order.delete()
        return Response({"message": "Order permanently deleted"}, status=status.HTTP_204_NO_CONTENT)