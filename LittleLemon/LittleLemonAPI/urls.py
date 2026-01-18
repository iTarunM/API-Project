from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

from rest_framework.authtoken.views import obtain_auth_token

# create a router for viewsets
router = DefaultRouter()
router.register(r"menu-items", views.MenuItemViewSet, basename="menuitem")

urlpatterns = [
    # menu items endpoints (using router)
    path("", include(router.urls)),
    # category endpoints
    path("categories/<int:pk>/", views.category_detail, name="category-detail"),
    # user group management endpoints
    path("groups/manager/users/", views.manager_group, name="manager-group"),
    path("groups/manager/users/<int:userId>/", views.manager_group_user),
    path("groups/delivery-crew/users/", views.delivery_crew_group),
    path("groups/delivery-crew/users/<int:userId>/", views.delivery_crew_group_user),
    # cart endpoints
    path("cart/menu-items/", views.cart, name="cart"),
    path("cart/menu-items/<int:cartItemId>/", views.cart_item, name="cart-item"),
    # order endpoints
    path("orders/", views.orders, name="orders"),
    path("orders/<int:orderId>/", views.order_detail, name="order-detail"),
    # html endpoints
    path("menu", views.menu_home, name="menu-home"),
    path("home", views.welcome, name="welcome"),
    # api test endpoints
    path("secret/", views.secret, name="secret"),
    path("me/", views.me, name="me"),
    path("throttle-check/", views.throttle_check, name="throttle-check"),
    path("throttle-check-auth/", views.throttle_check_auth, name="throttle-check-auth"),
    path("api-token-auth/", obtain_auth_token, name="api-token-auth"),
]
