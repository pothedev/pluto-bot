import os
import json
import requests

CONFIG_FILE = "./config.json"


# ------------------ config ------------------

def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump({}, f)
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

def ensure_server_config(guild_id):
    config = load_config()
    if str(guild_id) not in config:
        config[str(guild_id)] = {}
        save_config(config)

def set_server_setting(guild_id, key, value):
    config = load_config()
    config[str(guild_id)][key] = value
    save_config(config)
    


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

def is_bot_setup(guild_id):
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return False

    server_config = config.get(str(guild_id), {})

    required_keys = [
        "booster_role_id",
        "logs_channel_id",
        "bloxlink_api_key",
        "trello_api_key",
        "trello_token",
        "trello_board_id",
        "trello_list_id"
    ]

    return all(server_config.get(key) for key in required_keys)