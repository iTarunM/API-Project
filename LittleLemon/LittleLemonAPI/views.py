from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer, StaticHTMLRenderer
from rest_framework.decorators import (
    api_view,
    renderer_classes,
    permission_classes,
    throttle_classes,
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group

from .models import MenuItem, Category, Cart, CartItem, Order, OrderItem
from .throttles import FiveCallsPerMinute
from .serializers import (
    MenuItemSerializer,
    CategorySerializer,
    CartSerializer,
    CartItemSerializer,
    OrderSerializer,
    OrderItemSerializer,
    UserSerializer,
    GroupUserSerializer,
)


# utility functions for role checks and order retrieval
def is_manager(user):
    # check if user is in Manager group
    return user.groups.filter(name="Manager").exists()


def is_delivery_crew(user):
    # check if user is in Delivery crew group
    return user.groups.filter(name="Delivery crew").exists()


def is_customer(user):
    # check if user is a customer (no group assigned)
    return user.groups.count() == 0


def get_user_orders(user):
    # get orders based on user role
    if is_customer(user):
        return Order.objects.filter(user=user)
    elif is_manager(user):
        return Order.objects.all()
    elif is_delivery_crew(user):
        return Order.objects.filter(delivery_crew=user)
    return Order.objects.none()


def apply_order_filters_and_pagination(queryset, request):
    # apply filtering, ordering, and pagination to orders
    # filter by status
    status_param = request.query_params.get("status")
    if status_param is not None:
        try:
            queryset = queryset.filter(status=int(status_param))
        except ValueError:
            return None, Response(
                {"error": "Invalid status value"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    # apply ordering
    ordering = request.query_params.get("ordering", "-date")
    try:
        queryset = queryset.order_by(ordering)
    except:
        return None, Response(
            {"error": "Invalid ordering field"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # apply pagination
    page = request.query_params.get("page", 1)
    per_page = request.query_params.get("per_page", 5)
    try:
        page = int(page)
        per_page = int(per_page)
    except ValueError:
        return None, Response(
            {"error": "Invalid pagination parameters"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    start = (page - 1) * per_page
    end = start + per_page
    return (queryset, page, per_page, queryset[start:end]), None


def manage_group_members(request, group_name, is_post=False):
    # handle GET and POST for group management
    if not is_manager(request.user):
        return Response(
            {"error": "Only managers can access this endpoint"},
            status=status.HTTP_403_FORBIDDEN,
        )

    group = Group.objects.get(name=group_name)

    if request.method == "GET":
        members = User.objects.filter(groups__name=group_name)
        serializer = UserSerializer(members, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = GroupUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username"]
        user = get_object_or_404(User, username=username)
        group.user_set.add(user)
        return Response(
            {"message": f"User {username} added to {group_name} group"},
            status=status.HTTP_201_CREATED,
        )


# menu item viewset
class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ["price", "inventory", "title", "category__title"]
    search_fields = ["title", "category__title"]
    filterset_fields = ["category__title", "price"]
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def _check_manager_permission(self):
        if not is_manager(self.request.user):
            return Response(
                {"error": "Only managers can perform this action"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return None

    def create(self, request, *args, **kwargs):
        perm_error = self._check_manager_permission()
        if perm_error:
            return perm_error
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        perm_error = self._check_manager_permission()
        if perm_error:
            return perm_error
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        perm_error = self._check_manager_permission()
        if perm_error:
            return perm_error
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        perm_error = self._check_manager_permission()
        if perm_error:
            return perm_error
        return super().destroy(request, *args, **kwargs)

    def get_throttles(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            self.throttle_classes = [FiveCallsPerMinute]
        else:
            self.throttle_classes = [AnonRateThrottle]
        return [throttle() for throttle in self.throttle_classes]


# category detail view
@api_view(["GET"])
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    serializer = CategorySerializer(category)
    return Response(serializer.data)


# manager group management endpoints
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def manager_group(request):
    # manage manager group members
    return manage_group_members(request, "Manager")


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def manager_group_user(request, userId):
    # remove user from manager group
    if not is_manager(request.user):
        return Response(
            {"error": "Only managers can access this endpoint"},
            status=status.HTTP_403_FORBIDDEN,
        )
    user = get_object_or_404(User, id=userId)
    manager_group = Group.objects.get(name="Manager")
    manager_group.user_set.remove(user)
    return Response({"message": f"User {user.username} removed from managers group"})


# delivery crew group management endpoints
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def delivery_crew_group(request):
    # manage delivery crew members
    return manage_group_members(request, "Delivery crew")


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delivery_crew_group_user(request, userId):
    # remove user from delivery crew group
    if not is_manager(request.user):
        return Response(
            {"error": "Only managers can access this endpoint"},
            status=status.HTTP_403_FORBIDDEN,
        )
    user = get_object_or_404(User, id=userId)
    delivery_crew_group = Group.objects.get(name="Delivery crew")
    delivery_crew_group.user_set.remove(user)
    return Response(
        {"message": f"User {user.username} removed from delivery crew group"}
    )


# cart endpoints
@api_view(["GET", "POST", "DELETE"])
@permission_classes([IsAuthenticated])
def cart(request):
    # manage user shopping cart
    if not is_customer(request.user):
        return Response(
            {"error": "Only customers can access cart"},
            status=status.HTTP_403_FORBIDDEN,
        )

    user_cart, _ = Cart.objects.get_or_create(user=request.user)

    if request.method == "GET":
        serializer = CartSerializer(user_cart)
        return Response(serializer.data)

    elif request.method == "POST":
        menu_item_id = request.data.get("menu_item_id")
        quantity = request.data.get("quantity", 1)

        if not menu_item_id:
            return Response(
                {"error": "menu_item_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {"error": "quantity must be a positive integer"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        menu_item = get_object_or_404(MenuItem, id=menu_item_id)

        cart_item, created = CartItem.objects.get_or_create(
            cart=user_cart,
            menu_item=menu_item,
            defaults={
                "quantity": quantity,
                "unit_price": menu_item.price,
                "price": menu_item.price * quantity,
            },
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.price = cart_item.unit_price * cart_item.quantity
            cart_item.save()

        serializer = CartSerializer(user_cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    elif request.method == "DELETE":
        user_cart.items.all().delete()
        return Response({"message": "Cart cleared"})


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def cart_item(request, cartItemId):
    # remove specific item from cart
    if not is_customer(request.user):
        return Response(
            {"error": "Only customers can access cart"},
            status=status.HTTP_403_FORBIDDEN,
        )

    user_cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, id=cartItemId, cart=user_cart)
    cart_item.delete()
    return Response({"message": "Cart item removed"})


# order endpoints
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
@throttle_classes([FiveCallsPerMinute])
def orders(request):
    # GET or CREATE orders based on user role
    if request.method == "GET":
        orders_list = get_user_orders(request.user)
        if not orders_list:
            return Response(
                {"error": "Unauthorized"},
                status=status.HTTP_403_FORBIDDEN,
            )

        result, error = apply_order_filters_and_pagination(orders_list, request)
        if error:
            return error

        queryset, page, per_page, orders_page = result
        serializer = OrderSerializer(orders_page, many=True)
        return Response(
            {
                "total": queryset.count(),
                "page": page,
                "per_page": per_page,
                "orders": serializer.data,
            }
        )

    elif request.method == "POST":
        if not is_customer(request.user):
            return Response(
                {"error": "Only customers can create orders"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            user_cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response(
                {"error": "Cart is empty"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user_cart.items.count() == 0:
            return Response(
                {"error": "Cannot create order from empty cart"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        total = sum(item.price for item in user_cart.items.all())
        order = Order.objects.create(user=request.user, total=total)

        for cart_item in user_cart.items.all():
            OrderItem.objects.create(
                order=order,
                menu_item=cart_item.menu_item,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                price=cart_item.price,
            )

        user_cart.items.all().delete()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# order detail view
@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
@throttle_classes([FiveCallsPerMinute])
def order_detail(request, orderId):
    # manage individual orders
    order = get_object_or_404(Order, id=orderId)

    # check permissions
    if is_customer(request.user) and order.user != request.user:
        return Response(
            {"error": "You can only view your own orders"},
            status=status.HTTP_403_FORBIDDEN,
        )
    elif is_delivery_crew(request.user) and order.delivery_crew != request.user:
        return Response(
            {"error": "You can only view orders assigned to you"},
            status=status.HTTP_403_FORBIDDEN,
        )

    if request.method == "GET":
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    elif request.method in ["PUT", "PATCH"]:
        if is_manager(request.user):
            delivery_crew_id = request.data.get("delivery_crew_id")
            status_val = request.data.get("status")

            if delivery_crew_id is not None:
                try:
                    delivery_crew = User.objects.get(id=delivery_crew_id)
                    if not is_delivery_crew(delivery_crew):
                        return Response(
                            {"error": "User is not in delivery crew"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    order.delivery_crew = delivery_crew
                except User.DoesNotExist:
                    return Response(
                        {"error": "User not found"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            if status_val is not None:
                try:
                    status_val = int(status_val)
                    if status_val not in [0, 1]:
                        raise ValueError
                    order.status = status_val
                except (ValueError, TypeError):
                    return Response(
                        {"error": "Status must be 0 or 1"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            order.save()
            serializer = OrderSerializer(order)
            return Response(serializer.data)

        elif is_delivery_crew(request.user):
            if order.delivery_crew != request.user:
                return Response(
                    {"error": "You can only update orders assigned to you"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            status_val = request.data.get("status")
            if status_val is not None:
                try:
                    status_val = int(status_val)
                    if status_val not in [0, 1]:
                        raise ValueError
                    order.status = status_val
                except (ValueError, TypeError):
                    return Response(
                        {"error": "Status must be 0 or 1"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                order.save()

            serializer = OrderSerializer(order)
            return Response(serializer.data)

        else:
            return Response(
                {"error": "Customers cannot update orders"},
                status=status.HTTP_403_FORBIDDEN,
            )

    elif request.method == "DELETE":
        if not is_manager(request.user):
            return Response(
                {"error": "Only managers can delete orders"},
                status=status.HTTP_403_FORBIDDEN,
            )
        order.delete()
        return Response({"message": "Order deleted"}, status=status.HTTP_200_OK)


# test HTML endpoints
@api_view(["GET"])
@renderer_classes([StaticHTMLRenderer])
def welcome(request):
    html = "<html><body><h1>Welcome to Little Lemon API</h1></body></html>"
    return Response(html)


@api_view()
@renderer_classes([TemplateHTMLRenderer])
def menu_home(request):
    items = MenuItem.objects.select_related("category").all()
    serialized_item = MenuItemSerializer(items, many=True)
    return Response({"data": serialized_item.data}, template_name="menu.html")


# test endpoints
@api_view()
@permission_classes([IsAuthenticated])
def secret(request):
    return Response({"message": "This is a secret endpoint!"})


@api_view()
@permission_classes([IsAuthenticated])
def me(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view()
@throttle_classes([AnonRateThrottle])
def throttle_check(request):
    return Response({"message": "This is a throttled endpoint!"})


@api_view()
@permission_classes([IsAuthenticated])
@throttle_classes([FiveCallsPerMinute])
def throttle_check_auth(request):
    return Response({"message": "Authenticated users' throttled endpoint!"})
