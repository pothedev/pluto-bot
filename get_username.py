import requests
from data import SERVER_ID, BLOXLINK_API_KEY



def roblox_id_to_username(user_id):
  url = f"https://users.roblox.com/v1/users/{user_id}"
  response = requests.get(url)
  
  if response.status_code == 200:
    data = response.json()
    return data["name"]
  else:
    return None
  

def get_roblox_id(id):
  response = requests.get(f'https://api.blox.link/v4/public/guilds/{SERVER_ID}/discord-to-roblox/{id}',  headers={"Authorization" : BLOXLINK_API_KEY})
  if response.status_code == 200:
    new_id = response.json()["robloxID"]
    return new_id
  else: return None


def get_username(discord_id):
  return roblox_id_to_username(get_roblox_id(discord_id))





