from flask import Flask
import os
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "devsecret")

mongo_uri = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
client = MongoClient(mongo_uri)
db = client["sitstraight"]

@app.route("/")
def home():
    return "SitStraight Web App Running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
