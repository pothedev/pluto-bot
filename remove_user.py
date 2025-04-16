import requests
from get_cards import get_cards
from setup_functions import load_config



def remove_booster(user, guild_id):

  config = load_config()
  server_config = config.get(guild_id, {})

  trello_api_key = server_config["trello_api_key"]
  trello_token = server_config["trello_token"]

  user_id = get_cards(guild_id)[0][user]

  url = f"https://api.trello.com/1/cards/{user_id}"

  query = {
    'key': trello_api_key,
    'token': trello_token
  }

  print("removing", user, "as", user_id)

  response = requests.request(
    "DELETE",
    url,
    params=query
  )

  print("removed i think")
  
  if response.status_code == 404:
    print(response.text)
  elif response.status_code == 200:
    print("successfully removed user from trello board")
  else:
    print("some crazy error at remove booster")
    print(response.status_code)

