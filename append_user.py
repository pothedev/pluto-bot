import requests
from setup_functions import load_config

def append_booster(user, guild_id):

  config = load_config()
  server_config = config.get(guild_id, {})

  trello_list_id = server_config["trello_list_id"]
  trello_api_key = server_config["trello_api_key"]
  trello_token = server_config["trello_token"]

  url = "https://api.trello.com/1/cards"

  headers = {
    "Accept": "application/json"
  }

  query = {
    'idList': trello_list_id,
    'key': trello_api_key,
    'token': trello_token,
    'name': user
  }

  response = requests.request(
    "POST",
    url,
    headers=headers,
    params=query
  )

  
  if response.status_code == 404:
    print(response.text)
  elif response.status_code == 200:
    print("successfully appended user to trello board")

