"""
database.py

Simple MongoDB wrapper for saving posture data.
"""

from pymongo import MongoClient
import os
from datetime import datetime

class DatabaseClient:
    """
    Handles all database operations for the ML client.
    """

    def __init__(self):
        # Load MongoDB connection string from environment variables
        mongo_uri = os.getenv("MONGO_URI", "mongodb://mongodb:27017")

        # Connect to MongoDB
        client = MongoClient(mongo_uri)

        # Select database + collection
        self.db = client["sitstraight"]
        self.collection = self.db["posture"]

    def insert_posture(self, posture, metrics):
        """
        Inserts a new posture detection record into MongoDB.

        Args:
            posture (str): posture classification label
            metrics (dict): posture-related values
        """
        entry = {
            "timestamp": datetime.utcnow(),
            "posture": posture,
            "metrics": metrics
        }

        # Insert into MongoDB
        self.collection.insert_one(entry)
        print(f"[DB] Saved entry: {entry}")
