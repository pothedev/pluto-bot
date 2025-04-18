import requests
from functions.setup_functions import load_config


def get_cards(guild_id):

  config = load_config(guild_id)

  trello_api_key = config["trello_api_key"]
  trello_token = config["trello_token"]
  trello_list_id = config["trello_list_id"]

  url = f"https://api.trello.com/1/lists/{trello_list_id}/cards"

  headers = {
    "Accept": "application/json"
  }

  query = {
    'key': trello_api_key,
    'token': trello_token
  }

  response = requests.request(
    "GET",
    url,
    headers=headers,
    params=query
  )

  response = response.json()

  labels = []
  cards = {}

  for object in response: 
    labels.append(object['name'])
    cards[object['name']] = object['id']
  return [cards, labels]
