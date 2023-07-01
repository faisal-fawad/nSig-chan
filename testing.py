import requests

name = "luciangamer2"

# Search name
req = requests.post("https://api.brawltools.com/player/search", json={"query": name})
json = req.json()
print(json)


id = json["searchPlayers"][0]["player"]["smashId"]
print(req.json())

# 1 represents 1V1, 2 represents 2V2
for i in range(1, 3):
    req = requests.post("https://api.brawltools.com/player/pr", json={"entrantSmashIds": [id], "gameMode": i})
    print(req.json())