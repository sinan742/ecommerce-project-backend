from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Order, OrderItem
from products.models import Cart
from decimal import Decimal 
from .serializers import OrderItemSerializer,OrderSerializer
from django.core.mail import send_mail

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

        try:
            total_amount = sum(item.product.price * item.quantity for item in cart_items)
            
            shipping_charge = Decimal('50.00')
            final_total = total_amount + shipping_charge

            address = request.data.get('address')
            if not address:
                return Response({"error": "Address is required"}, status=status.HTTP_400_BAD_REQUEST)

            order = Order.objects.create(
                user=user,
                total_amount=float(final_total), 
                status = 'Order Placed',
                address=address,
                is_paid=False
            )
            for item in cart_items:

                product = item.product

                if product.stock < item.quantity:
                    return Response(
                        {"error": f"Not enough stock for {product.name}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Reduce stock
                product.stock -= item.quantity
                product.save()
            
           

            # email sending order
            if order:

                subject = f"Order Placed! Your Order #{order.id} is Confirmed"
                message = f"Hi {user.username},\n\nYour football gear is ready! We have received your order #{order.id}.\nTotal Amount: ₹{order.total_amount}\nAddress: {order.address}\n\nKeep playing!"
                recipient_list = [user.email]
                try:
                   send_mail(subject, message, 'your-email@gmail.com', recipient_list)
                except Exception as e:
                   print(f"Email failed: {e}")

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product_name=item.product.name, 
                    quantity=item.quantity,
                    price=float(item.product.price),
                    image=item.product.image
                )

            cart_items.delete()

            return Response({
                "message": "Order Placed Successfully (COD)",
                "order_id": order.id
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            print("SERVER ERROR:", str(e))
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)