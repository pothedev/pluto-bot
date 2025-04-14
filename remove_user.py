from data import TRELLO_API_KEY, TRELLO_TOKEN
import requests
from get_cards import get_cards


def remove_booster(user):

  user_id = get_cards()[0][user]

  url = f"https://api.trello.com/1/cards/{user_id}"

  query = {
    'key': TRELLO_API_KEY,
    'token': TRELLO_TOKEN
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

