from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Order, OrderItem
from products.models import Cart
from decimal import Decimal 
from .serializers import OrderItemSerializer,OrderSerializer
from django.core.mail import send_mail

from django.conf import settings 

class PlaceOrderCODView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
       user = request.user
       orders = Order.objects.filter(user=user).order_by('-created_at')
       serializer = OrderSerializer(orders, many=True, context={'request': request})
       return Response(serializer.data)
    
    def post(self, request):
        user = request.user
        cart_items = Cart.objects.filter(user=user)
        
        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. First Check Stock for all items
        for item in cart_items:
            if item.product.stock < item.quantity:
                return Response(
                    {"error": f"Not enough stock for {item.product.name}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        try:
            total_amount = sum(item.product.price * item.quantity for item in cart_items)
            shipping_charge = Decimal('50.00')
            final_total = total_amount + shipping_charge

            address = request.data.get('address')
            if not address:
                return Response({"error": "Address is required"}, status=status.HTTP_400_BAD_REQUEST)

            # 2. Create the Order
            order = Order.objects.create(
                user=user,
                total_amount=float(final_total), 
                status = 'Order Placed',
                address=address,
                is_paid=False
            )

            # 3. Create Order Items and Update Stock
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product_name=item.product.name, 
                    quantity=item.quantity,
                    price=float(item.product.price),
                    product_image=item.product.image
                )
                
                # Reduce stock
                product = item.product
                product.stock -= item.quantity
                product.save()

            # 4. Email sending logic (Moved after creating order items)
            subject = f"Order Placed! Your Order #{order.id} is Confirmed"
            message = (
                f"Hi {user.username},\n\n"
                f"Your football gear is ready! We have received your order #{order.id}.\n"
                f"Total Amount: ₹{order.total_amount}\n"
                f"Address: {order.address}\n\n"
                "Keep playing!"
            )
            recipient_list = [user.email]

            try:
                send_mail(
                    subject, 
                    message, 
                    settings.DEFAULT_FROM_EMAIL, 
                    recipient_list,
                    fail_silently=False
                )
            except Exception as e:
                print(f"Order Confirmation Email failed: {e}")

            # 5. Clear Cart
            cart_items.delete()

            return Response({
                "message": "Order Placed Successfully (COD)",
                "order_id": order.id
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            print("SERVER ERROR:", str(e))
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)