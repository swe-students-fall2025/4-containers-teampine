from pymongo import MongoClient
import os
import time

mongo_uri = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
client = MongoClient(mongo_uri)
db = client["sitstraight"]
collection = db["posture"]

print("ML client connected to MongoDB!")

while True:
    print("ML client heartbeat...")
    time.sleep(5)
