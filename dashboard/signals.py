from django.db.models.signals import pre_save,post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from order.models import Order

@receiver(pre_save, sender=User)
def notify_user_status_change(sender, instance, **kwargs):
    if instance.id is None:
        return

    try:
        previous_user = User.objects.get(pk=instance.id)
    except User.DoesNotExist:
        return

    if previous_user.is_active != instance.is_active:
        subject = "Account Status Updated - Beyond The Pitch"
        
        if instance.is_active:
            message = f"Hi {instance.username},\n\nYour account has been activated! You can now log in and shop for your favorite football gear."
        else:
            message = f"Hi {instance.username},\n\nYour account has been deactivated by the administrator. If you think this is a mistake, please contact support."

        # Send the email
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [instance.email],
            fail_silently=True,
        )

@receiver(post_save,sender=Order)
def send_order_status_mail(sender,instance,created,**kwargs):
    if not created:
        subject = f"Order #{instance.id} Status Updated"
        message = f"Hi {instance.user.username},\n\nYour order status has been updated to: {instance.status}.\n\nThank you for shopping with us!"
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [instance.user.email]

        try:
            send_mail(subject, message, email_from, recipient_list)
        except Exception as e:
            print(f" {e}")        