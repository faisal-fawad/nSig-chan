import requests
from bs4 import BeautifulSoup
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
full_data_set = []
i = 0
regions = ["us-e", "eu", "sea", "brz", "aus"]
game_modes = ["1v1", "2v2"]
for single_region in regions:
    for game_mode in game_modes:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Platform; Security; OS-or-CPU; Localization; rv:1.4) Gecko/20030624 Netscape/7.1 (ax)',
        }
        page = requests.get(f"https://www.brawlhalla.com/rankings/power/{game_mode}/{single_region}", headers=headers)
        soup = BeautifulSoup(page.content, "html.parser")
        rows = soup.findAll("tr", id=None)
        for one_row in rows:
            social_one = None
            social_two = None
            p_center_iteration = 0
            for one in one_row.findAll("td", class_="pcenter"):
                if p_center_iteration == 0:
                    rank = one
                elif p_center_iteration == 1:
                    top_8 = one
                elif p_center_iteration == 2:
                    top_32 = one
                elif p_center_iteration == 3:
                    gold = one
                elif p_center_iteration == 4:
                    silver = one
                elif p_center_iteration == 5:
                    bronze = one
                p_center_iteration += 1
            p_name_left_iteration = 0
            for one in one_row.findAll("td", class_="pnameleft"):
                if p_name_left_iteration == 0:
                    socials = one
                    for link in socials.findAll("a", href=True):
                        if 'twitter.com' in link["href"]:
                            social_one = link["href"]
                            # social_one = social_one[:4] + 's' + social_one[4:]  # Adding character 's' to http
                        elif 'twitch.tv' in link["href"]:
                            social_two = link["href"]
                            # social_two = social_two[:4] + 's' + social_two[4:]  # Adding character 's' to http
                if p_name_left_iteration == 1:
                    name = one
                p_name_left_iteration += 1
            earnings = one_row.find("td", style=True)
            real_region = single_region
            if real_region == "us-e":
                real_region = "na"
            elif real_region == "brz":
                real_region = "sa"
            player_data = next((pd for pd in full_data_set if pd["name"].lower() == name.text.lower()), None)
            if player_data is None:
                i += 1
                data_set = {"name": name.text, "id": i, "region": real_region,
                            "socials": [social_one, social_two], "earnings": earnings.text, "stats": [{
                                "gamemode": game_mode, "rank": rank.text, "placements": {
                                    "top_8": top_8.text, "top_32": top_32.text,
                                    "gold": gold.text, "silver": silver.text,
                                    "bronze": bronze.text}}]}
                full_data_set.append(data_set)
            else:
                new_data = {"gamemode": game_mode, "rank": rank.text, "placements": {
                                "top_8": top_8.text, "top_32": top_32.text,
                                "gold": gold.text, "silver": silver.text, "bronze": bronze.text}}
                player_data["stats"].append(new_data)

cluster = MongoClient(os.getenv("MONGO_TOKEN"))
db = cluster["website"]

if full_data_set:
    db["pr"].delete_many({})
    db["pr"].insert_many(full_data_set)
    print("Completed!")
else:
    print("Error!")