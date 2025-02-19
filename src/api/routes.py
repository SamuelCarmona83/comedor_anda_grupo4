from flask import request, jsonify, Blueprint
from api.models import db, User, Product, Order
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from api.utils import APIException
from datetime import datetime, timezone
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
import os

cloudinary.config(
    cloud_name="dnmm7omko",
    api_key="412312661645263",
    api_secret=os.getenv("CLOUDINARY_SECRET", ""),
    secure=True
)

api = Blueprint('api', __name__)

@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():
    response_body = {
        "message": "Hello! I'm a message that came from the backend."
    }
    return jsonify(response_body), 200

@api.route('/login', methods=['POST'])
def login():
    """
    Handle user login and return a JWT token with a redirect route based on user role.
    """
    body = request.get_json()

    # Validate input
    if not body or "email" not in body or "password" not in body:
        return jsonify({"msg": "Missing email or password"}), 400

    email = body.get("email")
    password = body.get("password")

    # Fetch the user from the database
    user = User.query.filter_by(email=email).first()

    if user and user.password == password:  # Password should ideally be hashed
        # Determine the redirect route based on user role
        if user.is_cliente:
            redirect_url = '/menu'
        elif user.is_cocina:
            redirect_url = '/dashboard/cocina'
        elif user.is_admin:
            redirect_url = '/dashboard/cocina'
        else:
            redirect_url = '/'  # Default route for unassigned roles

        # Generate a JWT token using a string for `identity` (e.g., `user.id`)
        access_token = create_access_token(identity=str(user.id))

        # Respond with the token and redirect URL
        return jsonify({"token": access_token, "redirect_url": redirect_url}), 200

    # Handle invalid credentials
    return jsonify({"msg": "Invalid email or password"}), 401

@api.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    """
    A protected route that requires a valid JWT token.
    """
    current_user = get_jwt_identity()
    return jsonify({"msg": "Access granted", "user": current_user}), 200

@api.route('/products', methods=['POST'])
def create_product():
    """
    Create a new product.
    """
    body = request.form

    # Validate required fields
    if not body or "name" not in body or "description" not in body or "type" not in body or "stock" not in body:
        raise APIException("Missing product field", status_code=400)

    name = body.get("name")
    description = body.get("description")
    type = body.get("type")
    stock = body.get("stock")

    # Log the received stock value for debugging
    print(f"Received stock value: {stock}")

    # Validate stock as a positive integer
    if not stock.isdigit() or int(stock) < 0:
        raise APIException("Invalid stock value", status_code=400)

    stock = int(stock)  # Convert stock to an integer after validation

    # Handle file upload for image
    image = request.files.get("image")
    if not image:
        raise APIException("Image is required", status_code=400)

    try:
        upload_result = cloudinary.uploader.upload(image)
        image_url = upload_result["secure_url"]
    except Exception as e:
        raise APIException(f"Error uploading image: {str(e)}", status_code=500)

    # Create new product
    new_product = Product(
        name=name, 
        description=description,
        type=type,
        stock=stock,
        is_active=True,  # Default to True for new products
        image=image_url
    )
    db.session.add(new_product)
    db.session.commit()

    return jsonify({"msg": "Product created successfully"}), 200

@api.route('/products', methods=['GET'])
def get_products():
    """
    Retrieve all products.
    """
    try:
        # Fetch all products from the database
        products = Product.query.all()

        # Handle the case when no products are found
        if not products:
            return jsonify({"message": "No products found"}), 404

        # Serialize the products for the response
        products_serialized = [product.serialize() for product in products]

        # Return the serialized products with a 200 status
        return jsonify({"products": products_serialized}), 200

    except Exception as e:
        # Log the exception for debugging
        print(f"Error in get_products: {e}")
        # Return a 500 error for internal server issues
        return jsonify({"msg": "Internal server error"}), 500


@api.route('/orders', methods=['POST'])
@jwt_required()
def create_order():
    """
    Create a new order for the logged-in user.
    """
    current_user_id = get_jwt_identity()  # This is now the user ID as a string
    user = User.query.get(current_user_id)  # Fetch the user object

    if not user:
        return jsonify({"msg": "User not found"}), 404

    body = request.get_json()

    # Validate required fields
    if not body or "product_id" not in body or "quantity" not in body:
        return jsonify({"msg": "Missing product_id or quantity"}), 400

    product_id = body.get("product_id")
    quantity = body.get("quantity")

    # Validate quantity
    if not isinstance(quantity, int) or quantity <= 0:
        return jsonify({"msg": "Quantity must be a positive integer"}), 400

    # Fetch product and check availability
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"msg": "Product not found"}), 404

    if product.stock < quantity:
        return jsonify({"msg": "Insufficient stock"}), 400

    # Deduct stock and create the order
    try:
        product.stock -= quantity
        order = Order(
            user_id=user.id,  # Use the user ID
            product_id=product_id,
            quantity=quantity,
            date=datetime.now(timezone.utc),  # Use timezone-aware datetime
            status="Pending"  # Default status
        )
        db.session.add(order)
        db.session.commit()

        return jsonify({"msg": "Order created successfully", "order": order.serialize()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Failed to create order: {str(e)}"}), 500
    
@api.route('/orders', methods=['GET'])
def get_all_orders():
    """
    Retrieve all orders from all users.
    This endpoint is now accessible to everyone, no authentication required.
    """
    try:
        # Fetch all orders
        orders = Order.query.all()

        # Handle the case when no orders are found
        if not orders:
            return jsonify({"message": "No orders found"}), 404

        # Serialize orders for response
        orders_serialized = [order.serialize() for order in orders]

        # Return the serialized orders with a 200 status
        return jsonify({"orders": orders_serialized}), 200

    except Exception as e:
        # Log the exception for debugging
        print(f"Error in get_all_orders: {e}")
        # Return a 500 error for internal server issues
        return jsonify({"msg": "Internal server error"}), 500