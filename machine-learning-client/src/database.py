"""
MongoDB database client for the ML client.
Handles storing posture samples.
"""

import os
import sys
from datetime import datetime, timezone
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure


# ============================================================
# MONGODB CONNECTION
# ============================================================

DEFAULT_DOCKER_URI = "mongodb://mongodb:27017"
DEFAULT_LOCAL_URI = "mongodb://127.0.0.1:27017"

MONGO_URI = os.getenv("MONGO_URI", DEFAULT_DOCKER_URI)


def connect_to_mongo(uri):
    """Connect to MongoDB with retry logic."""
    try:
        print(f"[DB] Attempting connection to: {uri[:50]}...")
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        print(f"[DB] ✓ Connected successfully!")
        return client
    except (ServerSelectionTimeoutError, ConnectionFailure) as error:
        print(f"[DB] ✗ Failed to connect")
        print(f"[DB] Error type: {type(error).__name__}")
        print(f"[DB] Error message: {str(error)}")
        # Try fallback to localhost
        if uri != DEFAULT_LOCAL_URI:
            print(f"[DB] Trying fallback → {DEFAULT_LOCAL_URI}")
            try:
                client = MongoClient(DEFAULT_LOCAL_URI, serverSelectionTimeoutMS=3000)
                client.admin.command("ping")
                print(f"[DB] Connected → {DEFAULT_LOCAL_URI}")
                return client
            except (ServerSelectionTimeoutError, ConnectionFailure):
                pass
        print("[DB] ERROR: Could not connect to MongoDB")
        sys.exit(1)


client = connect_to_mongo(MONGO_URI)
db = client["sitstraight"]
samples = db["posture_samples"]


# ============================================================
# DATABASE CLIENT CLASS
# ============================================================


class DatabaseClient:
    """Database client for ML posture tracking."""

    def __init__(self):
        self.samples = samples

    def insert_posture(self, posture_state, metrics):
        """Insert a posture sample into MongoDB."""
        try:
            doc = {
                "timestamp": datetime.now(timezone.utc),
                "state": posture_state,
                "score": metrics.get("score", 0),
                "slouch": metrics.get("slouch_raw", 0),
                "head_tilt": metrics.get("head_tilt", 0),
                "shoulder_angle": metrics.get("shoulder_angle", 0),
                "torso_angle": metrics.get("torso_angle", 0),
            }
            self.samples.insert_one(doc)
            print(f"[DB] Saved: {posture_state} | score={metrics.get('score', 0)}")
        except Exception as error:
            print(f"[DB ERROR] Failed to save: {error}")

