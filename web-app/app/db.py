"""
Unified MongoDB helper for SitStraight.
Handles:
 - User accounts
 - Posture sample saving
 - Safe MongoDB connection (Docker or localhost)
"""
import os
import re
import sys
from datetime import datetime, timezone
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
from werkzeug.security import generate_password_hash, check_password_hash


# ============================================================
# SMART MONGO URI SELECTION (Docker OR local)
# ============================================================

DEFAULT_DOCKER_URI = "mongodb://mongodb:27017"
DEFAULT_LOCAL_URI = "mongodb://127.0.0.1:27017"

env_uri = os.getenv("MONGO_URI", DEFAULT_DOCKER_URI)


def choose_uri(uri: str) -> str:
    """Try connecting to the provided URI; fallback to localhost."""
    try:
        test = MongoClient(uri, serverSelectionTimeoutMS=5000)
        test.admin.command("ping")
        print(f"[DB] Connected → {uri}")
        return uri
    except Exception as e:
        print(f"[DB] Failed → {uri}")
        print(f"[DB] Error: {type(e).__name__}: {str(e)}")
        print(f"[DB] Switching to localhost.")
        return DEFAULT_LOCAL_URI


MONGO_URI = choose_uri(env_uri)


# ============================================================
# CONNECT TO MONGODB
# ============================================================

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    client.admin.command("ping")
    print("[DB] Connection OK")
except (ServerSelectionTimeoutError, ConnectionFailure):
    print("[DB] ERROR: Could not connect to:", MONGO_URI)
    sys.exit(1)

db = client["sitstraight"]

users = db["users"]
samples = db["posture_samples"]


# ============================================================
# EMAIL + PASSWORD VALIDATION
# ============================================================


def is_valid_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None


def is_strong_password(password):
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain an uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain a lowercase letter."
    if not re.search(r"[0-9]", password):
        return False, "Password must contain a number."
    return True, None


# ============================================================
# USER MANAGEMENT
# ============================================================


def create_user(name, email, password):
    """Create a new user in MongoDB."""

    if not name or name.strip() == "":
        return False, "Name cannot be empty."

    if not email or not is_valid_email(email):
        return False, "Invalid email format."

    email = email.strip().lower()

    if users.find_one({"email": email}):
        return False, "Email already registered."

    strong, msg = is_strong_password(password)
    if not strong:
        return False, msg

    hashed_pw = generate_password_hash(password)

    users.insert_one(
        {
            "name": name.strip(),
            "email": email,
            "password": hashed_pw,
        }
    )

    return True, None


def validate_user(email, password):
    """Validate a user login."""
    if not email or not password:
        return False, "All fields are required."

    email = email.strip().lower()
    user = users.find_one({"email": email})

    if not user:
        return False, "Email not found."

    if not check_password_hash(user["password"], password):
        return False, "Incorrect password."

    return True, user


# ============================================================
# POSTURE SAMPLE SAVING
# ============================================================


def save_posture_sample(data):
    """Insert posture analysis into MongoDB."""
    try:
        doc = {
            "timestamp": datetime.now(timezone.utc),
            "score": data.get("score"),
            "state": data.get("state"),
            "slouch": data.get("slouch", data.get("slouch_raw", 0)),
        }
        samples.insert_one(doc)
        print("[DB] Saved posture:", doc)
    except Exception as e:
        print("[DB ERROR] Saving failed:", e)
