# db.py
# Handles MongoDB connection and user-related helper functions

# app/db.py

"""MongoDB helper functions for SitStraight."""

import os
import re
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash


# ===============================
# CONNECT TO MONGODB
# ===============================
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)

db = client["sitstraight"]
users = db["users"]   # Collection where users are stored


# ===============================
# Helper — Validate Email Format
# ===============================
def is_valid_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None


# ===============================
# Helper — Validate Password Strength
# (you can customize the rules if needed)
# ===============================
def is_strong_password(password):
    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."

    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number."

    return True, None


# ===============================
# Create a New User
# ===============================
def create_user(name, email, password):
    """Create a new user and store in MongoDB."""

    if not name or name.strip() == "":
        return False, "Name cannot be empty."

    if not email or not is_valid_email(email):
        return False, "Invalid email format."

    email = email.strip().lower()  # Normalize email

    # Check if email exists already
    if users.find_one({"email": email}):
        return False, "Email is already registered."

    # Validate password strength
    strong, msg = is_strong_password(password)
    if not strong:
        return False, msg

    hashed_pw = generate_password_hash(password)

    users.insert_one({
        "name": name.strip(),
        "email": email,
        "password": hashed_pw,
    })

    return True, None


# ===============================
# Validate User Login
# ===============================
def validate_user(email, password):
    """Validate user credentials against MongoDB."""
    if not email or not password:
        return False, "All fields are required."

    email = email.strip().lower()

    user = users.find_one({"email": email})
    if not user:
        return False, "Email not found."

    if not check_password_hash(user["password"], password):
        return False, "Incorrect password."

    return True, user
