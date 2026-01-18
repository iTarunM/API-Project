from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

# Models for Little Lemon API


# Category modelclass for menu item categories
class Category(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Categories"


# Menu item model for food items
class MenuItem(models.Model):
    title = models.CharField(max_length=255, unique=True)
    price = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(2.00)]
    )
    inventory = models.SmallIntegerField(validators=[MinValueValidator(0)])
    category = models.ForeignKey(Category, on_delete=models.PROTECT, default=1)

    def __str__(self):
        return self.title


# Cart model for user food shopping carts
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username}"


# Cart item model for items in the cart
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.title} in {self.cart.user.username}'s cart"


# Order model for user orders
class Order(models.Model):
    STATUS_CHOICES = [
        (0, "Pending"),
        (1, "Delivered"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    delivery_crew = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_orders",
        limit_choices_to={"groups__name": "Delivery crew"},
    )
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=0)
    total = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


# Order item model for items in an order
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="order_items"
    )
    menu_item = models.ForeignKey(MenuItem, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.title} in Order {self.order.id}"
