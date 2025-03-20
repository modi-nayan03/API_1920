from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.errors import InvalidId  # Import InvalidId
from flask_cors import CORS # Import CORS
from functools import wraps

app = Flask(__name__)
bcrypt = Bcrypt(app)
CORS(app)  # Enable CORS for your app
# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client['1920']
admin_collection = db['admin']
appointment_collection = db['appointment']
artist_collection = db['artist']
category_collection = db['category']


# Admin Registration API
@app.route("/api/admin/register", methods=["POST"])
def register_admin():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Missing JSON data"}), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"message": "All fields are required"}), 400

    if admin_collection.find_one({"email": email}):
        return jsonify({"message": "Admin already exists"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    admin_data = {
        "name": name,
        "email": email,
        "password": hashed_password,
        "role": "admin"
    }

    admin_collection.insert_one(admin_data)
    return jsonify({"message": "Admin registered successfully"}), 201


# Admin Login API
@app.route("/api/admin/login", methods=["POST", "OPTIONS"])
def admin_login():
    if request.method == "OPTIONS":
        # Comprehensive CORS preflight response
        response = jsonify({"message": "CORS preflight passed"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Accept")
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response, 200

    data = request.get_json()
    if not data:
        return jsonify({"message": "Missing JSON data"}), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    admin = admin_collection.find_one({"email": email})

    if not admin or not bcrypt.check_password_hash(admin["password"], password):
        return jsonify({"message": "Invalid email or password"}), 401

    return jsonify({
        "message": "Login successful",
        "admin_name": admin["name"]
    }), 200


@app.route("/api/admin/appoinment", methods=["POST"])
def admin_appoinment():
    data = request.json
    Client_name = data.get("Client_name")
    Mobile_no = data.get("Mobile_no")
    Email_address = data.get("Email_address")
    Date = data.get("Date")
    Time_slot = data.get("Time_slot")
    How_did_you_hear_about_us = data.get("How_did_you_hear_about_us")
    Message = data.get("Message")
    Reference_image = data.get("Reference_image")

    if not Client_name or not Mobile_no or not Email_address or not Date or not Time_slot or not How_did_you_hear_about_us or not Message or not Reference_image:
        return jsonify({"message": "All fields are required"}), 400

    appoinment_data = {
        "Client_name": Client_name,
        "Mobile_no": Mobile_no,
        "Email_address": Email_address,
        "Date": Date,
        "Time_slot": Time_slot,
        "How_did_you_hear_about_us": How_did_you_hear_about_us,
        "Message": Message,
        "Reference_image": Reference_image
    }

    appointment_collection.insert_one(appoinment_data)
    return jsonify({"message": "Appoinment created successfully"}), 201


@app.route("/api/admin/appoinment", methods=["GET"])
def admin_appoinment_get():
    try:
        appoinments = list(appointment_collection.find())
        # Convert ObjectId to string for JSON serialization
        for appoinment in appoinments:
            appoinment['_id'] = str(appoinment['_id'])
        return jsonify(appoinments), 200
    except Exception as e:
        return jsonify({"message": "Error fetching appointments", "error": str(e)}), 500


@app.route("/api/admin/appoinment/<string:appoinment_id>", methods=["GET"])
def admin_appoinment_get_by_id(appoinment_id):
    try:
        appoinment = appointment_collection.find_one({"_id": ObjectId(appoinment_id)})
        if not appoinment:
            return jsonify({"message": "Appointment not found"}), 404
        appoinment['_id'] = str(appoinment['_id'])
        return jsonify(appoinment), 200
    except InvalidId:  # Catch the specific exception
        return jsonify({"message": "Invalid Appointment ID format"}), 400
    except Exception as e:
        return jsonify({"message": "Error fetching appointment", "error": str(e)}), 500


@app.route("/api/admin/artist", methods=["POST"])
def admin_artist():
    data = request.json
    artist_name = data.get("artist_name")
    artist_bio = data.get("artist_bio")
    artist_portfolio_desc = data.get("artist_portfolio_desc")
    artist_image = data.get("artist_image")
    artist_image_name = data.get("artist_image_name")

    if not artist_name or not artist_bio or not artist_portfolio_desc or not artist_image or not artist_image_name:
        return jsonify({"message": "All fields are required"}), 400

    artist_data = {
        "artist_name": artist_name,
        "artist_bio": artist_bio,
        "artist_portfolio_desc": artist_portfolio_desc,
        "artist_image": artist_image,
        "artist_image_name": artist_image_name

    }

    artist_collection.insert_one(artist_data)
    return jsonify({"message": "Artist created successfully"}), 201


@app.route("/api/admin/artist", methods=["GET"])
def admin_artist_get():
    try:
        artists = list(artist_collection.find())
        # Convert ObjectId to string for JSON serialization
        for artist in artists:
            artist['_id'] = str(artist['_id'])
        return jsonify(artists), 200
    except Exception as e:
        return jsonify({"message": "Error fetching artists", "error": str(e)}), 500


@app.route("/api/admin/portfolio", methods=["GET"])
def admin_artist_portfolio():
    try:
        # Get all artists with their portfolio information
        artists = list(artist_collection.find())

        # Convert ObjectId to string and format portfolio data
        portfolios = []
        for artist in artists:
            portfolio = {
                "artist_id": str(artist['_id']),
                "artist_name": artist['artist_name'],
                "artist_bio": artist['artist_bio'],
                "artist_portfolio_desc": artist['artist_portfolio_desc'],
                "artist_image": artist['artist_image'],
                "artist_image_name": artist['artist_image_name']
            }
            portfolios.append(portfolio)

        return jsonify(portfolios), 200
    except Exception as e:
        return jsonify({"message": "Error fetching portfolios", "error": str(e)}), 500


@app.route("/api/admin/category", methods=["POST"])
def admin_category():
    data = request.json
    category_name = data.get("category_name")
    category_image = data.get("category_image")
    category_image_name = data.get("category_image_name")
    selected_artists = data.get("selected_artists", [])  # List of artist IDs to include

    # Check if category name already exists
    if category_collection.find_one({"category_name": category_name}):
        return jsonify({"message": "Category already exists"}), 400

    # Create category data
    category_data = {
        "category_name": category_name,
        "category_image": category_image,
        "category_image_name": category_image_name,
        "artists": []  # Initialize empty artists array
    }

    # Add only selected artists to category
    for artist_id in selected_artists:
        try: # Add try-except block
            artist = artist_collection.find_one({"_id": ObjectId(artist_id)})
            if artist:
                artist_ref = {
                    "artist_id": str(artist["_id"]),
                    "artist_name": artist["artist_name"]
                }
                category_data["artists"].append(artist_ref)
        except InvalidId:
            return jsonify({"message": f"Invalid artist ID: {artist_id}"}), 400


    # Insert category with selected artist data
    category_collection.insert_one(category_data)
    return jsonify({"message": "Category created successfully"}), 201


# Add GET endpoint for categories
@app.route("/api/admin/category", methods=["GET"])
def get_categories():
    try:
        categories = list(category_collection.find())
        # Convert ObjectId to string for JSON serialization
        for category in categories:
            category['_id'] = str(category['_id'])
        return jsonify(categories), 200
    except Exception as e:
        return jsonify({"message": "Error fetching categories", "error": str(e)}), 500


@app.route("/api/admin/dashboard", methods=["GET"])
def admin_dashboard():
    email = request.headers.get('email')
    admin = admin_collection.find_one({"email": email})

    if not admin:
        return jsonify({"message": "Admin not found"}), 404

    return jsonify({
        "message": "Admin access granted",
        "admin_name": admin["name"],
        "email": admin["email"]
    }), 200


if __name__ == "__main__":
    app.run(debug=True)