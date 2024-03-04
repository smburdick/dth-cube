import requests
import os
import time
import json
from types import SimpleNamespace

BUDGET_USD = 5
COLORS = ["W", "U", "B", "R", "G", "GOLD", "COLORLESS"]
COLORS = list(map(lambda x: x.lower(), COLORS))
CMCS = list(range(1,7))
CARD_TYPES = ["creature", "enchantment", "artifact", "instant", "sorcery"]

def cacheScryfallJSON() -> dict[str, SimpleNamespace]:
  # Get all the creatures in local files
  cards = {}
  if not os.path.exists("scryfall-cache"):
    os.makedirs("scryfall-cache")
  for color in COLORS:
    for cmc in CMCS:
      for cardType in CARD_TYPES:
        path = f"cards/{color}/{cmc}/{color}-{cmc}-{cardType}.txt"
        for cardName in open(path, "r").read().splitlines():
          if cardName in cards or cardName.isspace() or len(cardName) == 0: # Skip duplicates and whitespace
            continue
          apiCardName = cardName.replace(" ", "+").replace("//", "") # Replace spaces with + and remove slashes form double faced cards
          if not os.path.isfile("scryfall-cache/" + apiCardName + ".json"):
            time.sleep(0.05)
            api_url = f"https://api.scryfall.com/cards/named?fuzzy={apiCardName}"
            response = requests.get(api_url)
            if response.status_code == 200:
              with open("scryfall-cache/" + apiCardName + ".json", "w+") as f:
                data = json.loads(response.text)
                f.write(json.dumps(data, indent=2))
            else:
              print(f"Failed to cache {cardName} with status code {response.status_code}")
              continue
          data = open("scryfall-cache/" + apiCardName + ".json", "r").read()
          data = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))
          priceOptions = ["usd", "usd_foil", "usd_etched", "usd_foil_etched"]
          # TODO: Add price filtering
          # for p in priceOptions:
          #   if p in data.prices:
          #     if float(data.prices[p]) > BUDGET_USD:
          #       print(f"Skipping {cardName} with price {data.prices.usd}")
          #       continue
          if int(data.cmc) != cmc:
            print(data.name, int(data.cmc), cmc)
          # assert (data.colors[0].lower() == color) or (color == "gold" and len(data.colors) > 1)
          cards[cardName] = data
  return cards

def analyzeCreatureTypes(cards: dict[str, SimpleNamespace]) -> dict[str, int]:
  creatureTypes = open("tribes.txt", "r").read().splitlines()
  for c in creatureTypes:
    if c.isspace() or len(c) == 0:
      creatureTypes.remove(c)
  creatureTypes = {tribe: 0 for tribe in creatureTypes}
  for card in cards.values():
    if "Creature" in card.type_line:
      for subtype in card.type_line.split("—")[1].split(" "):
        if subtype in creatureTypes:
          creatureTypes[subtype] += 1
        # elif subtype != "" and not subtype.isspace():
        #   raise ValueError(f"Unknown subtype {subtype} in {card.name}")
  return creatureTypes
  
if __name__ == "__main__":
  cardData = cacheScryfallJSON()
  data = analyzeCreatureTypes(cardData)
  data = {k: v for k, v in sorted(data.items(), key=lambda item: item[1])}
  print(json.dumps(data, indent=2), "\ntotal: ", sum(map(lambda x: x[1], data.items())))
