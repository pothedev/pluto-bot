import os
import json
import requests

from functions.firebase_config import db


CONFIG_FILE = "./config.json"


def load_server_config(guild_id):
    doc_ref = db.collection("config").document(str(guild_id))
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    return {}



# ------------------ config ------------------

def load_config(guild_id):
    guild_id = str(guild_id)

    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            server_config = load_server_config(guild_id)
            if not server_config:
                json.dump({}, f)
            else:
                json.dump({guild_id: server_config}, f)

    try:
        with open(CONFIG_FILE, "r") as f:
            content = f.read().strip()
            config = json.loads(content if content else "{}")
    except json.JSONDecodeError:
        config = {}

    # fallback if guild config is missing
    if guild_id not in config:
        server_config = load_server_config(guild_id)
        if server_config:
            config[guild_id] = server_config
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=2)

    return config.get(guild_id, {})

    

def save_config(data):
    # Save to local JSON file
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

    # Also update to Firestore per guild
    for guild_id, guild_data in data.items():
        doc_ref = db.collection("config").document(guild_id)
        doc_ref.set(guild_data, merge=True)


def set_server_setting(guild_id, key, value):
    try:
        with open(CONFIG_FILE, "r") as f:
            content = f.read().strip()
            all_config = json.loads(content if content else "{}")
    except (FileNotFoundError, json.JSONDecodeError):
        all_config = {}

    guild_id = str(guild_id)

    if guild_id not in all_config:
        all_config[guild_id] = {}

    all_config[guild_id][key] = value
    save_config(all_config)


    


# ------------------ validation ------------------

def validate_trello_key(key):
    try:
        r = requests.get("https://api.trello.com/1/members/me", params={"key": key})
        return r.status_code in (200, 400)
    except:
        return False

def validate_trello_token(key, token):
    try:
        r = requests.get("https://api.trello.com/1/members/me", params={"key": key, "token": token})
        print(r.status_code)
        return int(r.status_code) == 200
    except:
        return False

def validate_trello_board(key, token, board_id):
    r = requests.get(f"https://api.trello.com/1/boards/{board_id}", params={"key": key, "token": token})
    return r.status_code == 200

def validate_trello_list(key, token, list_id):
    r = requests.get(f"https://api.trello.com/1/lists/{list_id}", params={"key": key, "token": token})
    return r.status_code == 200



#---------------------- is set up ----------------------------

from functions.firebase_config import db 

def is_bot_setup(guild_id):
    guild_id = str(guild_id)

    # try loading from local JSON
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        config = {}

    server_config = config.get(guild_id, {})

    required_keys = [
        "booster_role_id",
        "logs_channel_id",
        "bloxlink_api_key",
        "trello_api_key",
        "trello_token",
        "trello_board_id",
        "trello_list_id"
    ]

    # if local config is incomplete or missing
    if not all(server_config.get(key) for key in required_keys):
        # try fetching from Firestore
        doc = db.collection("config").document(guild_id).get()
        if doc.exists:
            server_config = doc.to_dict()

            # also optionally save to local file
            config[guild_id] = server_config
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=2)

            # return True if Firebase config is complete
            return all(server_config.get(key) for key in required_keys)
        else:
            return False  # not found in Firebase either

    return True  # local config is valid



def is_ping_cd_channel_set(guild_id):
    guild_id = str(guild_id)

    # try loading from local JSON
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        config = {}

    server_config = config.get(guild_id, {})

    # check if key exists locally
    if not server_config.get("ping_cd_channel_id"):
        # try fetching from Firestore
        doc = db.collection("config").document(guild_id).get()
        if doc.exists:
            server_config = doc.to_dict()

            # optionally update local cache
            config[guild_id] = server_config
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=2)

            return bool(server_config.get("ping_cd_channel_id"))
        else:
            return False  # not found in Firebase either

    return True  # local config has the key


def is_staff_role_set(guild_id):
    guild_id = str(guild_id)

    # try loading from local JSON
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        config = {}

    server_config = config.get(guild_id, {})

    # check if key exists locally
    if not server_config.get("staff_role_id"):
        # try fetching from Firestore
        doc = db.collection("config").document(guild_id).get()
        if doc.exists:
            server_config = doc.to_dict()

            # optionally update local cache
            config[guild_id] = server_config
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=2)

            return bool(server_config.get("staff_role_id"))
        else:
            return False  # not found in Firebase either

    return True  # local config has the key

