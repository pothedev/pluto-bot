import requests
from setup_functions import load_config



def roblox_id_to_username(user_id):
  url = f"https://users.roblox.com/v1/users/{user_id}"
  response = requests.get(url)
  
  if response.status_code == 200:
    data = response.json()
    return data["name"]
  else:
    return None
  

def get_roblox_id(id, guild_id):

  config = load_config()
  server_config = config.get(guild_id, {})
  bloxlink_api_key = server_config["bloxlink_api_key"]

  response = requests.get(f'https://api.blox.link/v4/public/guilds/{guild_id}/discord-to-roblox/{id}',  headers={"Authorization" : bloxlink_api_key})
  if response.status_code == 200:
    new_id = response.json()["robloxID"]
    return new_id
  else: return None


def get_username(discord_id, guild_id):
  return roblox_id_to_username(get_roblox_id(discord_id, guild_id))





