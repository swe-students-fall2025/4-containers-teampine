"""Database helper for saving posture samples."""

import os
from datetime import datetime
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
client = MongoClient(MONGO_URI)
db = client["sitstraight"]
samples = db["posture_samples"]

def save_posture_sample(data):
    """Insert a posture sample into MongoDB."""
    doc = {
        "timestamp": datetime.utcnow(),
        "score": data["score"],
        "state": data["state"],
        "slouch": data.get("slouch", 0),
    }
    samples.insert_one(doc)
