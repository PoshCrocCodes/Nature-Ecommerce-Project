import uuid
from django.db import models
from django.contrib.auth.models import User
from products.models import Product


def generate_tracking_code():
    return 'GH' + str(uuid.uuid4()).upper().replace('-', '')[:8]


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def subtotal(self):
        return self.product.price * self.quantity


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Order Placed'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing Your Order'),
        ('ready', 'Ready for Collection/Dispatch'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    DELIVERY_CHOICES = [
        ('delivery', 'Home Delivery'),
        ('collection', 'Click & Collect'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    tracking_code = models.CharField(max_length=20, unique=True, default=generate_tracking_code)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default='delivery')
    delivery_address = models.TextField(blank=True)
    delivery_city = models.CharField(max_length=100, blank=True)
    delivery_postcode = models.CharField(max_length=10, blank=True)
    notes = models.TextField(blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2, default=3.99)
    scheduled_delivery = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.tracking_code} - {self.user.username}"

    @property
    def grand_total(self):
        if self.delivery_method == 'collection':
            return self.total_price
        return self.total_price + self.delivery_fee

    @property
    def status_step(self):
        """Returns 0-5 step number for progress bar."""
        steps = {
            'pending': 0,
            'confirmed': 1,
            'preparing': 2,
            'ready': 3,
            'out_for_delivery': 4,
            'delivered': 5,
        }
        return steps.get(self.status, 0)

    @property
    def status_percentage(self):
        """Returns percentage completion (0-100) for progress bar."""
        return min((self.status_step / 5) * 100, 100)

    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=200)  # snapshot at time of order
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # price at time of order

    def __str__(self):
        return f"{self.quantity}x {self.product_name}"

    @property
    def subtotal(self):
        return self.price * self.quantity
