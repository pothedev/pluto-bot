import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

# Read the stringified JSON from environment
firebase_config_json = os.getenv("FIREBASE_CONFIG_JSON")

# Parse it from JSON string to dict
firebase_dict = json.loads(firebase_config_json)

# Correct usage: pass dict, not string
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()
