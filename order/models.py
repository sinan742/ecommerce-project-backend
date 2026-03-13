from django.db import models
from django.contrib.auth.models import User
import uuid # 🛑 Unique ID generate cheyyaan

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.FloatField()
    is_paid = models.BooleanField(default=False)
    address = models.TextField()
    phone = models.CharField(max_length=15, null=True, blank=True)
    
    created_at = models.DateField(auto_now_add=True)
    
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Order Placed', 'Order Placed'),
        ('Packed','Packed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending') 

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE) 
    product_name = models.CharField(max_length=200)
    quantity = models.IntegerField(default=1)
    price = models.FloatField()
    image = models.URLField(max_length=800, null=True, blank=True)