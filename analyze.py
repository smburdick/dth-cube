import requests
import os
import time
import json
from types import SimpleNamespace
import matplotlib.pyplot as plt

DEBUG = False

def log(*msg):
  if DEBUG:
    print(msg)

BUDGET_USD = 5
COLORS = ["W", "U", "B", "R", "G", "GOLD", "COLORLESS"]
CMCS = list(range(1,7))
CARD_TYPES = ["creature", "enchantment", "artifact", "instant", "sorcery"]
EXCEPTIONS = [
  "Era of Enlightenment // Hand of Enlightenment",
  "Heliod, the Radiant Dawn // Heliod, the Warped Eclipse",
  "The Kami War // O-Kagachi Made Manifest",
  "Walking Bulwark",
  "Okiba Reckoner Raid // Nezumi Road Captain"
]

def cacheScryfallJSON() -> dict[str, SimpleNamespace]:
  # Get all the creatures in local files
  cards = {}
  if not os.path.exists("scryfall-cache"):
    os.makedirs("scryfall-cache")
  for color in list(map(lambda x: x.lower(), COLORS)):
    for cmc in CMCS:
      for cardType in CARD_TYPES:
        path = f"cards/{color}/{cmc}/{color}-{cmc}-{cardType}.txt"
        for cardName in open(path, "r").read().splitlines():
          if cardName in cards or cardName.isspace() or len(cardName) == 0: # Skip duplicates and whitespace
            continue
          apiCardName = cardName.replace(" ", "+").replace("//", "") # Replace spaces with + and remove slashes form double faced cards
          fname = "scryfall-cache/" + apiCardName + ".json"
          if not os.path.isfile(fname):
            time.sleep(0.05)
            api_url = f"https://api.scryfall.com/cards/named?fuzzy={apiCardName}"
            response = requests.get(api_url)
            if response.status_code == 200:
              with open(fname, "w+") as f:
                data = json.loads(response.text)
                f.write(json.dumps(data, indent=2))
            else:
              print(f"Failed to cache {cardName} with status code {response.status_code}")
              continue
          data = open(fname, "r").read()
          data = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))
          priceData = data.prices
          prices = [priceData.usd, priceData.usd_foil, priceData.usd_etched]
          isOverbudget = all([p != None and float(p) > BUDGET_USD for p in prices])
          if isOverbudget:
            log(f"{cardName} is over-budget.")
            continue
          if int(data.cmc) != cmc:
            log(data.name, int(data.cmc), cmc)
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
      sentinel = False
      for subtype in card.type_line.split("—")[1].split(" "):
        if subtype == "" or subtype.isspace():
          continue
        if subtype in creatureTypes:
          creatureTypes[subtype] += 1
          sentinel = True
      if not sentinel and card.name not in EXCEPTIONS:
        print(f"Failed to find subtype for {card.name}")

  return creatureTypes

def analyzeNoncreatureTypes(cards: dict[str, SimpleNamespace]) -> dict[str, int]:
  noncreatureTypes = ['Instant', 'Sorcery', 'Enchantment', 'Artifact']
  noncreatureTypes = {type: 0 for type in noncreatureTypes}
  for card in cards.values():
    for type in noncreatureTypes:
      if type in card.type_line:
        noncreatureTypes[type] += 1
  return noncreatureTypes

def analyzeColorDistribution(cards: dict[str, SimpleNamespace]) -> dict[str, int]:
  colorDistribution = {color: 0 for color in COLORS}
  colorDistribution["GOLD"] = {}
  for card in cards.values():
    if len(card.color_identity) == 0:
      colorDistribution["COLORLESS"] += 1
    elif len(card.color_identity) > 1:
      s = str(frozenset(set(card.color_identity)))
      colorDistribution["GOLD"][s] = colorDistribution["GOLD"].get(s, 0) + 1
    else:
      color = card.color_identity[0]
      colorDistribution[color] += 1
  data = colorDistribution["GOLD"].copy()
  log("gold distribution: ", json.dumps(data, indent=2))
  _, ax = plt.subplots()
  colorDistribution.pop("GOLD")
  colorDistribution.pop("COLORLESS")
  ax.bar(colorDistribution.keys(), colorDistribution.values())
  plt.show()
  return colorDistribution
  
if __name__ == "__main__":
  cardData = cacheScryfallJSON()
  data = analyzeCreatureTypes(cardData)
  data = {k: v for k, v in sorted(data.items(), key=lambda item: item[1])}
  log("creatures: ", json.dumps(data, indent=2), "\ntotal: ", sum(map(lambda x: x[1], data.items())))
  data = analyzeNoncreatureTypes(cardData)
  log("noncreatures: ", json.dumps(data, indent=2), "\ntotal: ", sum(map(lambda x: x[1], data.items())))
  data = analyzeColorDistribution(cardData)
