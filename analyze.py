import requests
import os
import time
import json
from types import SimpleNamespace


COLORS = ["W", "U", "B", "R", "G", "GOLD", "COLORLESS"]
COLORS = list(map(lambda x: x.lower(), COLORS))
CMCS = list(range(1,7))
CARD_TYPES = ["creature", "enchantment", "artifact", "instant", "sorcery"]

def cacheScryfallJSON():
  # Get all the creatures in local files
  cards = {}
  for color in COLORS:
    for cmc in CMCS:
      for cardType in CARD_TYPES:
        path = f"{color}/{cmc}/{color}-{cmc}-{cardType}.txt"
        for cardName in open(path, "r").read().splitlines():
          if cardName in cards or cardName.isspace(): # Skip duplicates and whitespace
            continue
          apiCardName = cardName.replace(" ", "+").replace("//", "") # Replace spaces with + and remove slashes form double faced cards
          if not os.path.isfile("scryfall-cache/" + apiCardName + ".json"):
            time.sleep(0.1)
            api_url = f"https://api.scryfall.com/cards/named?fuzzy={apiCardName}"
            last_request = time.time()
            response = requests.get(api_url)
            if response.status_code == 200:
              with open("scryfall-cache/" + apiCardName + ".json", "w+") as f:
                f.write(response.text)
            else:
              print(f"Failed to cache {cardName} with status code {response.status_code}")
              continue
          data = open("scryfall-cache/" + apiCardName + ".json", "r").read()
          cards[cardName] = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))
  return cards
  
  
if __name__ == "__main__":
  d = cacheScryfallJSON()
