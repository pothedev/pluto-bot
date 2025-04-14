from data import TRELLO_BOOSTERS_LIST_ID, TRELLO_API_KEY, TRELLO_TOKEN
import requests

def append_booster(user):

  url = "https://api.trello.com/1/cards"

  headers = {
    "Accept": "application/json"
  }

  query = {
    'idList': TRELLO_BOOSTERS_LIST_ID,
    'key': TRELLO_API_KEY,
    'token': TRELLO_TOKEN,
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

