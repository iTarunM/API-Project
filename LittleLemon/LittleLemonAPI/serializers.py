from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from decimal import Decimal
from .models import MenuItem, Category, Cart, CartItem, Order, OrderItem
from django.contrib.auth.models import User
import bleach


# serializers for Little Lemon API
# Category serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "slug", "title"]


# Menu item serializer
class MenuItemSerializer(serializers.ModelSerializer):
    title = serializers.CharField(
        validators=[UniqueValidator(queryset=MenuItem.objects.all())]
    )
    price = serializers.DecimalField(
        max_digits=6, decimal_places=2, min_value=Decimal("0.00")
    )
    stock = serializers.IntegerField(source="inventory", min_value=0)
    price_after_tax = serializers.SerializerMethodField(method_name="calculate_tax")
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)

    def validate_title(self, value):
        return bleach.clean(value)

    class Meta:
        model = MenuItem
        fields = [
            "id",
            "title",
            "price",
            "stock",
            "price_after_tax",
            "category",
            "category_id",
        ]

    def calculate_tax(self, product: MenuItem):
        return round(product.price * Decimal(1.1), 2)


# Cart item serializers
class CartItemSerializer(serializers.ModelSerializer):
    menu_item = MenuItemSerializer(read_only=True)
    menu_item_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "menu_item", "menu_item_id", "quantity", "unit_price", "price"]
        read_only_fields = ["unit_price", "price"]


# Cart serializer
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "items", "total"]

    def get_total(self, obj):
        return sum(item.price for item in obj.items.all())


# Order item serializers
class OrderItemSerializer(serializers.ModelSerializer):
    menu_item = MenuItemSerializer(read_only=True)
    menu_item_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "menu_item", "menu_item_id", "quantity", "unit_price", "price"]
        read_only_fields = ["unit_price", "price"]


# Order serializer
class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    delivery_crew = serializers.StringRelatedField(read_only=True)
    delivery_crew_id = serializers.IntegerField(
        write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "delivery_crew",
            "delivery_crew_id",
            "status",
            "total",
            "date",
            "order_items",
        ]
        read_only_fields = ["user", "date", "total"]


# User serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


# serializer for adding/removing users to/from groups
class GroupUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)

    def validate_username(self, value):
        try:
            User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")
        return value
