import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from dotenv import load_dotenv


load_dotenv()

firebase_config = os.getenv("FIREBASE_CONFIG_JSON")
firebase_dict = json.loads(firebase_config)


if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()
