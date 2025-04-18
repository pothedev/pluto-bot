import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

# Get the raw JSON string from env
firebase_config_json = os.getenv("FIREBASE_CONFIG_JSON")

# Convert it to a dictionary
firebase_dict = json.loads(firebase_config_json)

# Initialize Firebase only once
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()
