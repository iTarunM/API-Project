# Little Lemon Restaurant Order Management API

A comprehensive REST API backend for a Little Lemon restaurant order management system built with Django and Django REST Framework. 

Little Lemon's online-based order management system. This is back-end API that allows customers to browse food items, view the item of the day and place orders. Managers need to be able to update the item of the day and monitor orders and assign deliveries. And the delivery crew should be able to check the orders assigned to them and update an order once it’s delivered

# Prerequisites
- Python 3.13+
- Virtual environment
- All dependencies installed

# Setup
1. Install/verify dependencies
   `../APIs/LittleLemon`

2. Run Migrations (if needed)
   run (venv) `python manage.py makemigrations`
   run (venv) `python manage.py migrate`

3. Create Test Data
   run (venv) `python setup_test_data.py`

4. Start Development Server
   run (venv) `python manage.py runserver 8000`

5. Access the API
- API Base: http://127.0.0.1:8000/api/
- Admin Panel: http://127.0.0.1:8000/admin/
- Browsable API: http://127.0.0.1:8000/api/menu-items/

# User roles/groups
1. Manager:
- Manage menu items (add, edit, delete)
- Assign users to delivery crew
- View all orders
- Assign delivery crew to orders
- Update order status

2. Customer (default role):
- Browse and search menu items
- Add items to shopping cart
- Place orders
- View own orders and status
- Track deliveries

3. Delivery Crew:
- View assigned orders
- Update order status (mark delivered)
- Track delivery progress

# Authentication
Token-based authentication with automatic token generation:

1. Register
POST /auth/users/
{
  "username": "john_doe",
  "password": "john_does_password",
  "email": "john_doe@littlelemon.com"
}

2. Login
POST /auth/token/login/
{
  "username": "john_doe",
  "password": "john_does_password"
}

3. Use in requests
Authorization: Token abc123def456ghi789jkl012mno345pqr678 (example)

# Core features implemented
1. User registration and token authentication
2. Djoser endpoints for user management
3. Menu items with CRUD operations
4. Role-based access control (3 roles)
5. Shopping cart with cart items
6. Order management with order items
7. User group assignment (Manager, Delivery Crew)
8. Order filtering and sorting
9. Pagination (menu items and orders)
10. Searching and filtering
11. Automatic cart clearing on order
12. Delivery crew assignment
13. Order status tracking
14. Throttling (5 calls/minute)
15. Proper HTTP status codes
16. Error handling and validation
17. Admin interface
18. Test data setup script

# 1. Menu Management
GET    /api/menu-items/              # list with filtering
POST   /api/menu-items/              # create (manager only)
GET    /api/menu-items/{id}/         # get single menu item
PUT    /api/menu-items/{id}/         # update (manager only)
DELETE /api/menu-items/{id}/         # delete (manager only)
Features:
- Filter by category and price
- Search by title
- Sorting and pagination
- Tax calculation

# 2. Shopping Cart
GET    /api/cart/menu-items/         # view cart
POST   /api/cart/menu-items/         # add item
DELETE /api/cart/menu-items/         # clear cart
DELETE /api/cart/menu-items/{id}/    # remove item
Features:
- One cart per customer
- Automatic quantity handling
- Auto-clear on order creation
- Total price calculation

# 3. Order Management
GET    /api/orders/                  # list orders
POST   /api/orders/                  # place order
GET    /api/orders/{id}/             # get order details
PATCH  /api/orders/{id}/             # update status
DELETE /api/orders/{id}/             # delete (manager only)
Features:
- Filter by status
- Sort by date
- Pagination
- Role-based access
- Delivery crew assignment

# User groups
GET    /api/groups/manager/users/                  # list managers
POST   /api/groups/manager/users/                  # add manager
DELETE /api/groups/manager/users/{id}/             # remove manager
GET    /api/groups/delivery-crew/users/            # list crew
POST   /api/groups/delivery-crew/users/            # add crew
DELETE /api/groups/delivery-crew/users/{id}/       # remove crew

# Database models
- MenuItem: Menu items with prices and inventory
- Category: Item categories
- Cart: Shopping cart (user)
- CartItem: Items in cart
- Order: Customer orders
- OrderItem: Items in order

# Configuration
- Authentication: Token-based only
- Throttling: 5 requests/minute (all users)
- Pagination: 5 items per page (default)
- Database: SQLite
- Status Codes: Full compliance (200, 201, 400, 403, 404, 429)

# Test data

| Username        | Password                  | Role          |
|-----------------|---------------------------|---------------|
| john_doe        | john_does_password        | Manager       |
| sarah_mitchell  | sarah_mitchells_password  | Customer      |
| david_chen      | david_chens_password      | Customer      |
| maria_garcia    | maria_garcias_password    | Delivery Crew |
| robert_thompson | robert_thompsons_password | Delivery Crew |

# Complete orrder flow
1. Customer registers: Gets auth token
2. Customer browses: GET /api/menu-items/
3. Customer adds to cart: POST /api/cart/menu-items/
4. Customer places: order POST /api/orders/
5. Cart auto-clears: No manual action needed
6. Manager assigns crew: PATCH /api/orders/{id}/
7. Delivery crew updates: PATCH /api/orders/{id}/ (status only)
8. Customer sees status: GET /api/orders/

# Security features
- Token-based authentication (no session auth)
- Role-based access control
- Rate limiting (5 requests/minute)
- Input validation
- Cross-site scripting protection (bleach library)
- Proper error handling

# Project files of interest
LittleLemon/
├── README.md (this file)
├── setup_test_data.py (to create test data in the db)
├── manage.py
├── db.sqlite3
├── LittleLemon/
│   ├── settings.py
│   ├── urls.py
└── LittleLemonAPI/
    ├── models.py
    ├── views.py
    ├── serializers.py
    ├── urls.py
    ├── admin.py
    ├── throttles.py


# Testing

The Django development server running on `http://127.0.0.1:8000/`


# 1. Get authentication tokens

For Manager:
```bash
curl -X POST http://127.0.0.1:8000/auth/token/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"john_doe","password":"john_does_password"}'
```

For Customer:
```bash
curl -X POST http://127.0.0.1:8000/auth/token/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"sarah_mitchell","password":"sarah_mitchells_password"}'
```

For Delivery Crew:
```bash
curl -X POST http://127.0.0.1:8000/auth/token/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"maria_garcia","password":"maria_garcias_password"}'
```

# 2. Test menu items (GET)

```bash
# get all menu items
curl -X GET http://127.0.0.1:8000/api/menu-items/ \
  -H "Authorization: Token SUPER_USER_TOKEN"

# filter by category
curl -X GET "http://127.0.0.1:8000/api/menu-items/?category__title=Main%20Courses" \
  -H "Authorization: Token SUPER_USER_TOKEN"

# search by title
curl -X GET "http://127.0.0.1:8000/api/menu-items/?search=salmon" \
  -H "Authorization: Token SUPER_USER_TOKEN"

# get single menu item
curl -X GET http://127.0.0.1:8000/api/menu-items/1/ \
  -H "Authorization: Token SUPER_USER_TOKEN"
```

# 3. Manager: create menu item

```bash
curl -X POST http://127.0.0.1:8000/api/menu-items/ \
  -H "Authorization: Token JOHN_DOES_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Risotto Milanese",
    "price": "15.99",
    "inventory": 10,
    "category_id": 2
  }'
```

# 4. Manager: assign delivery crew

```bash
curl -X POST http://127.0.0.1:8000/api/groups/delivery-crew/users/ \
  -H "Authorization: Token JOHN_DOES_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username":"maria_garcia"}'
```

# 5. Customer: add item to cart

```bash
curl -X POST http://127.0.0.1:8000/api/cart/menu-items/ \
  -H "Authorization: Token SARAH_MITCHELL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"menu_item_id":1,"quantity":2}'
```

# 6. Customer: view cart

```bash
curl -X GET http://127.0.0.1:8000/api/cart/menu-items/ \
  -H "Authorization: Token SARAH_MITCHELL_TOKEN"
```

# 7. Customer: place order

```bash
curl -X POST http://127.0.0.1:8000/api/orders/ \
  -H "Authorization: Token SARAH_MITCHELL_TOKEN" \
  -H "Content-Type: application/json"
```

# 8. Customer: view own orders

```bash
curl -X GET http://127.0.0.1:8001/api/orders/ \
  -H "Authorization: Token SARAH_MITCHELL_TOKEN"

# filter by status (0=Pending, 1=Delivered)
curl -X GET "http://127.0.0.1:8000/api/orders/?status=0" \
  -H "Authorization: Token SARAH_MITCHELL_TOKEN"
```

# 9. Manager: view all orders

```bash
curl -X GET http://127.0.0.1:8001/api/orders/ \
  -H "Authorization: Token JOHN_DOES_TOKEN"

# filter by status
curl -X GET "http://127.0.0.1:8000/api/orders/?status=0" \
  -H "Authorization: Token JOHN_DOES_TOKEN"
```

# 10. Manager: assign delivery crew to order

```bash
curl -X PATCH http://127.0.0.1:8001/api/orders/1/ \
  -H "Authorization: Token JOHN_DOES_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"delivery_crew_id":4}'
```

# 11. Manager: update order status

```bash
curl -X PATCH http://127.0.0.1:8000/api/orders/1/ \
  -H "Authorization: Token JOHN_DOES_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status":0}'
```

# 12. Delivery Crew: view assigned orders

```bash
curl -X GET http://127.0.0.1:8001/api/orders/ \
  -H "Authorization: Token MARIA_GARCIAS_TOKEN"
```

# 13. Delivery Crew: mark order as delivered

```bash
curl -X PATCH http://127.0.0.1:8000/api/orders/1/ \
  -H "Authorization: Token MARIA_GARCIAS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status":1}'
```

# 14. Manager: get group information

```bash
# Get all managers
curl -X GET http://127.0.0.1:8000/api/groups/manager/users/ \
  -H "Authorization: Token JOHN_DOES_TOKEN"

# Get all delivery crew
curl -X GET http://127.0.0.1:8000/api/groups/delivery-crew/users/ \
  -H "Authorization: Token JOHN_DOES_TOKEN"
```

# 15. Manager: remove user from group

```bash
# Remove from manager group
curl -X DELETE http://127.0.0.1:8000/api/groups/manager/users/2/ \
  -H "Authorization: Token JOHN_DOES_TOKEN"

# Remove from delivery crew
curl -X DELETE http://127.0.0.1:8000/api/groups/delivery-crew/users/4/ \
  -H "Authorization: Token JOHN_DOES_TOKEN"
```

# Available User IDs
Use the Django admin panel at http://127.0.0.1:8000/admin/ to see user IDs

# Default credentials:
- Username: admin (or your superuser username)
- Password: (as set during setup)

# Testing throttling
All endpoints enforce 5 requests per minute throttling. After 5 requests, you'll get:
```json
{
  "detail": "Request was throttled. Expected available in 59 seconds."
}
```

# Response Format Examples
1. Success Response (GET Menu Items)
```json
{
  "total": 9,
  "page": 1,
  "per_page": 5,
  "orders": [
    {
      "id": 1,
      "title": "Bruschetta",
      "price": "8.50",
      "stock": 20,
      "price_after_tax": "9.35",
      "category": {
        "id": 1,
        "slug": "appetizers",
        "title": "Appetizers"
      }
    }
  ]
}
```

2. Error Response (Unauthorized)
```json
{
  "error": "Only managers can add menu items"
}
```

## Common Status Codes

| Code | Meaning           | Example                        |
|------|-------------------|--------------------------------|
| 200  | Success           | GET request returned data      |
| 201  | Created           | POST request created resource  |
| 400  | Bad Request       | Invalid data in POST/PUT/PATCH |
| 403  | Forbidden         | User lacks permission          |
| 404  | Not Found         | Resource doesn't exist         |
| 429  | Too Many Requests | Rate limit exceeded            |

## Browsable API
The Django REST Framework Browsable API is available at:
- http://127.0.0.1:8000/api/menu-items/
- http://127.0.0.1:8000/api/orders/
- http://127.0.0.1:8000/api/cart/menu-items/

Use your browser with appropriate authentication token in the header to test interactively in Insomia.

## Admin Panel
Access Django admin at:
http://127.0.0.1:8000/admin/

Manage:
- Users
- Groups
- Menu Items
- Categories
- Carts
- Orders
