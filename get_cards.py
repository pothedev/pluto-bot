import requests
from data import TRELLO_API_KEY, TRELLO_TOKEN, TRELLO_BOOSTERS_LIST_ID


def get_cards():
  url = f"https://api.trello.com/1/lists/{TRELLO_BOOSTERS_LIST_ID}/cards"

  headers = {
    "Accept": "application/json"
  }

  query = {
    'key': TRELLO_API_KEY,
    'token': TRELLO_TOKEN
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
