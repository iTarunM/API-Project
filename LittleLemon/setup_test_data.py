#!/usr/bin/env python

# Setup script to create test data for the Little Lemon API.
# This script creates:
#   test users (customers, managers, delivery crew)
#   menu items and categories
#   tokens for testing

import os
import sys
import django

# add the project directory to the Python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LittleLemon.settings")
django.setup()

from django.contrib.auth.models import User, Group
from LittleLemonAPI.models import MenuItem, Category
from rest_framework.authtoken.models import Token


# create test data for the API
def create_test_data():
    # create groups if they don't exist
    manager_group, _ = Group.objects.get_or_create(name="Manager")
    delivery_group, _ = Group.objects.get_or_create(name="Delivery crew")
    print("Groups created/verified")

    # create test users
    # super user needs to be created manually from the admin panel
    users = [
        {
            "username": "john_doe",
            "password": "john_does_password",
            "email": "john_doe@littlelemon.com",
            "group": "Manager",
        },
        {
            "username": "sarah_mitchell",
            "password": "sarah_mitchells_password",
            "email": "sarah_mitchell@xyz.com",
            "group": None,
        },
        {
            "username": "david_chen",
            "password": "david_chens_password",
            "email": "david_chen@xyz.com",
            "group": None,
        },
        {
            "username": "maria_garcia",
            "password": "maria_garcias_password",
            "email": "maria_garcia@delivery.com",
            "group": "Delivery crew",
        },
        {
            "username": "robert_thompson",
            "password": "robert_thompsons_password",
            "email": "robert_thompson@delivery.com",
            "group": "Delivery crew",
        },
    ]

    for user_data in users:
        user, created = User.objects.get_or_create(
            username=user_data["username"],
            defaults={
                "email": user_data["email"],
                "first_name": user_data["username"].title().split("_")[0],
                "last_name": user_data["username"].title().split("_")[1],
            },
        )
        if created:
            user.set_password(user_data["password"])
            user.save()
            if user_data["group"]:
                group = Group.objects.get(name=user_data["group"])
                user.groups.add(group)
            print(f"Created user: {user_data['username']}")

        # create token
        Token.objects.get_or_create(user=user)

    # create categories
    categories_data = [
        {"title": "Appetizers", "slug": "appetizers"},
        {"title": "Main Courses", "slug": "main-courses"},
        {"title": "Desserts", "slug": "desserts"},
        {"title": "Beverages", "slug": "beverages"},
    ]

    categories = {}
    for cat_data in categories_data:
        cat, created = Category.objects.get_or_create(
            slug=cat_data["slug"], defaults={"title": cat_data["title"]}
        )
        categories[cat.id] = cat
        if created:
            print(f"✓ Created category: {cat_data['title']}")

    # create menu items
    menu_items = [
        {
            "title": "Bruschetta",
            "price": 8.50,
            "inventory": 20,
            "category": list(categories.values())[0],
        },
        {
            "title": "Calamari Fritti",
            "price": 10.00,
            "inventory": 15,
            "category": list(categories.values())[0],
        },
        {
            "title": "Grilled Salmon",
            "price": 18.50,
            "inventory": 10,
            "category": list(categories.values())[1],
        },
        {
            "title": "Pasta Carbonara",
            "price": 14.00,
            "inventory": 12,
            "category": list(categories.values())[1],
        },
        {
            "title": "Margherita Pizza",
            "price": 12.00,
            "inventory": 8,
            "category": list(categories.values())[1],
        },
        {
            "title": "Tiramisu",
            "price": 6.50,
            "inventory": 25,
            "category": list(categories.values())[2],
        },
        {
            "title": "Panna Cotta",
            "price": 5.50,
            "inventory": 20,
            "category": list(categories.values())[2],
        },
        {
            "title": "Espresso",
            "price": 3.00,
            "inventory": 50,
            "category": list(categories.values())[3],
        },
        {
            "title": "Italian Wine",
            "price": 8.00,
            "inventory": 30,
            "category": list(categories.values())[3],
        },
    ]

    for item_data in menu_items:
        item, created = MenuItem.objects.get_or_create(
            title=item_data["title"],
            defaults={
                "price": item_data["price"],
                "inventory": item_data["inventory"],
                "category": item_data["category"],
            },
        )
        if created:
            print(f"Created menu item: {item_data['title']}")

    print("\nTest data creation completed!")


if __name__ == "__main__":
    create_test_data()
