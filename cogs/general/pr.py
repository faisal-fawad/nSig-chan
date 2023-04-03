from bs4 import BeautifulSoup
import requests
import orjson as json
import re
from pymongo import MongoClient
import os
from universal import *


cluster = MongoClient(os.getenv("MONGO_TOKEN"))
db = cluster["website"]


async def grab_rest(data_set, all_data):
    other_data = None
    if data_set["gamemode"] == '1v1':
        mode = '2v2'
    elif data_set["gamemode"] == '2v2':
        mode = '1v1'
    for person in all_data:
        if person["name"].lower() == data_set["name"].lower():
            if person["gamemode"] == mode:
                other_data = person
    return other_data


async def create_pr_embed(mode_data, full_data):
    name = full_data["name"]
    region = full_data["region"]
    money_made = full_data["earnings"]
    twitter, twitch = full_data["socials"][0], full_data["socials"][1]
    rank = mode_data["rank"]
    gamemode = mode_data["gamemode"]
    top_8 = mode_data["placements"]["top_8"]
    top_32 = mode_data["placements"]["top_32"]
    gold = mode_data["placements"]["gold"]
    silver = mode_data["placements"]["silver"]
    bronze = mode_data["placements"]["bronze"]

    full_embed = discord.Embed(colour=discord.Colour.green(), title=f'Statistics for {name}',
                               timestamp=datetime.now(tz),
                               description=f'**PR:** {rank} \n'
                                           f'**Region:** {region.upper()} \n'
                                           f'**Mode:** {gamemode}')
    full_embed.add_field(name=f'Placements:', value=f'**Earnings:** {money_made} \n'
                                                    f'**Top 8:** {top_8} \n'
                                                    f'**Top 32:** {top_32}', inline=True)
    full_embed.add_field(name=f'Medals:', value=f'**Gold:** 🥇 {gold} \n'
                                                f'**Silver:** 🥈 {silver} \n'
                                                f'**Bronze:** 🥉 {bronze}', inline=True)
    full_embed.add_field(name=f'Socials:', value=f'**Twitter:** {twitter} \n'
                                                 f'**Twitch:** {twitch}', inline=False)
    return full_embed


async def create_stats_embed(data, name):
    def make_ordinal(n):
        n = int(n)
        if 11 <= (n % 100) <= 13:
            suffix = 'th'
        else:
            suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
        return str(n) + suffix
    tournaments = data['tournaments']

    pages = []
    split_tournaments = [tournaments[x:x + 3] for x in range(0, len(tournaments), 3)]
    for section in split_tournaments:
        full_description = f'**Aliases:** {", ".join(data["names"])}\n\n'
        for tournament in section:
            tourney_name = tournament['name']
            sets_lost = []
            i = 0
            for single_set in tournament["sets"]:
                single_set = single_set["score"]
                sides = single_set.split(' - ')
                if single_set == 'DQ':
                    sets_lost.append('DQ')
                    i += 1
                else:
                    for side in sides:
                        if tourney_name in side:
                            score_one = side.split(' ')[-1]
                            side_one = side.rstrip(side[-1])
                            side_one = side_one.strip()
                        else:
                            score_two = side.split(' ')[-1]
                            side_two = side.rstrip(side[-1])
                            side_two = side_two.strip()
                    try:
                        if int(score_one) < int(score_two):
                            sets_lost.append(f'{side_one} **{score_one} - {score_two}** {side_two}')
                            i += 1
                    except ValueError:
                        if score_one == 'L':
                            sets_lost.append(f'{side_one} **{score_one} - {score_two}** {side_two}')
                            i += 1
                if i == 2:
                    break
            time = datetime.utcfromtimestamp(tournament["time"]).strftime('%m/%d/%Y')
            if len(sets_lost) == 0:
                sets_lost = 'None'
            else:
                sets_lost = '\n'.join(sets_lost)
            tournament_string = f'**[{tournament["tourney"]}]({tournament["url"]})** \n' \
                                f'**Date:** {time} \n' \
                                f'**Seed:** {tournament["seed"]} \n' \
                                f'**Placement:** {make_ordinal(tournament["placement"])} \n' \
                                f'**Sets Lost:** \n{sets_lost}\n \n'
            full_description = full_description + tournament_string
        full_embed = discord.Embed(colour=discord.Colour.green(), title=f'Recent tournament history for {name}',
                                   timestamp=datetime.now(tz), description=full_description)
        pages.append(full_embed)
    return pages


class PowerButtons(discord.ui.View):
    def __init__(self, ctx, embeds, response, pages):
        super().__init__(timeout=300)
        self.response = response
        self.ctx = ctx
        self.embeds = embeds
        self.pages = pages
        self.page_number = 0
        if type(pages) == list:
            self.max_page = len(pages) - 1
        else:
            self.max_page = 0

    async def on_timeout(self):
        self.clear_items()
        await self.response.edit(view=self)

    async def interaction_check(self, interaction) -> bool:
        if interaction.user != self.ctx.author:
            return False
        else:
            return True

    @discord.ui.button(label='1v1', style=discord.ButtonStyle.green, custom_id='1', disabled=True)
    async def power_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        for one in self.children:
            if one.custom_id == '2':
                one.disabled = False
            if one.custom_id == '3':
                one.disabled = True
            if one.custom_id == '4':
                one.disabled = False
            if one.custom_id == '5':
                one.disabled = True
        button.disabled = True
        await interaction.response.edit_message(embed=self.embeds[0], view=self)

    @discord.ui.button(label='2v2', style=discord.ButtonStyle.green, custom_id='2')
    async def power_2(self, interaction: discord.Interaction, button: discord.ui.Button):
        for one in self.children:
            if one.custom_id == '1':
                one.disabled = False
            if one.custom_id == '3':
                one.disabled = True
            if one.custom_id == '4':
                one.disabled = False
            if one.custom_id == '5':
                one.disabled = True
        button.disabled = True
        await interaction.response.edit_message(embed=self.embeds[1], view=self)

    @discord.ui.button(label='<<', style=discord.ButtonStyle.green, custom_id='3', disabled=True)
    async def power_3(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page_number = self.page_number - 1
        if self.page_number < 0:
            self.page_number = 0
        if self.page_number == 0:
            button.disabled = True
        else:
            button.disabled = False
        for one in self.children:
            if one.custom_id == '4':
                one.disabled = True
            if one.custom_id == '5':
                one.disabled = False
        await interaction.response.edit_message(embed=self.pages[self.page_number], view=self)

    @discord.ui.button(label='Stats', style=discord.ButtonStyle.green, custom_id='4')
    async def power_4(self, interaction: discord.Interaction, button: discord.ui.Button):
        if type(self.pages) != list:
            embed = self.pages
        else:
            embed = self.pages[self.page_number]
        for one in self.children:
            if one.custom_id == '1':
                one.disabled = False
            if one.custom_id == '2':
                one.disabled = False
            if self.max_page == 0:
                if one.custom_id == '3':
                    one.disabled = True
                if one.custom_id == '5':
                    one.disabled = True
            elif self.max_page > 0:
                if one.custom_id == '3':
                    one.disabled = True
                if one.custom_id == '5':
                    one.disabled = False
        button.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label='>>', style=discord.ButtonStyle.green, custom_id='5', disabled=True)
    async def power_5(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page_number = self.page_number + 1
        if self.page_number > self.max_page:
            self.page_number = self.max_page
        if self.page_number == self.max_page:
            button.disabled = True
        else:
            button.disabled = False
        for one in self.children:
            if one.custom_id == '4':
                one.disabled = True
            if one.custom_id == '3':
                one.disabled = False
        await interaction.response.edit_message(embed=self.pages[self.page_number], view=self)


class Pr(commands.Cog, name="PR"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name='pr', with_app_command=True, aliases=['powerrank'],
                             description=f'Shows power ranking of a user', usage='(name)')
    @app_commands.describe(name='The name of the user')
    @app_commands.guilds(discord.Object(id=int(os.getenv('NSIG_SERVER'))))
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def pr(self, ctx, *, name=None):
        embed = discord.Embed(timestamp=datetime.now(tz), description=f'**Loading...**',
                              colour=theme)
        msg = await ctx.reply(embed=embed)
        if name is None:
            name = ctx.author.name
        if len(ctx.message.mentions) > 0:
            for one in ctx.message.mentions:
                name = re.sub(f'<@{one.id}>', one.name, name)

        pr_data = db["pr"].find_one({"name": {"$regex": "^{}$".format(name), "$options": "i"}})
        ranked_1v1 = False
        ranked_2v2 = False
        stats_rec = False
        if pr_data:
            try:
                key = pr_data["stats_id"]
                stats_rec = True
            except KeyError:
                pass
            for i in range(len(pr_data["stats"])):
                if pr_data["stats"][i]["gamemode"] == "1v1":
                    embed_1v1 = pr_data["stats"][i]
                    ranked_1v1 = True
                elif pr_data["stats"][i]["gamemode"] == "2v2":
                    embed_2v2 = pr_data["stats"][i]
                    ranked_2v2 = True
        if stats_rec:
            stats_data = db["stats"].find_one({"id": key})
            if stats_data:
                stats_rec = True
            else:
                stats_rec = False
        else:
            stats_data = db["stats"].find_one({"name": {"$regex": "^{}$".format(name), "$options": "i"}})
            if stats_data:
                stats_rec = True
            else:
                stats_rec = False

        if ranked_1v1 is False:
            power_1v1 = discord.Embed(timestamp=datetime.now(tz), description=f'**{name} is not power ranked in 1v1**',
                                      colour=error_colour)
        else:
            power_1v1 = await create_pr_embed(embed_1v1, pr_data)
        if ranked_2v2 is False:
            power_2v2 = discord.Embed(timestamp=datetime.now(tz), description=f'**{name} is not power ranked in 2v2**',
                                      colour=error_colour)
        else:
            power_2v2 = await create_pr_embed(embed_2v2, pr_data)
        if stats_rec is False:
            pages = discord.Embed(timestamp=datetime.now(tz),
                                  description=f'**{name} has no recent tournament history**',
                                  colour=error_colour)
        else:
            pages = await create_stats_embed(stats_data, name)
        await msg.edit(embed=power_1v1, view=PowerButtons(embeds=[power_1v1, power_2v2], pages=pages,
                                                          ctx=ctx, response=msg))

    @commands.hybrid_command(name='earnings', with_app_command=True,
                             description=f'Shows earnings of a user', usage='(name)')
    @app_commands.describe(name='The name of the user')
    @app_commands.guilds(discord.Object(id=int(os.getenv('NSIG_SERVER'))))
    async def earnings(self, ctx, *, name=None):
        if len(ctx.message.mentions) > 0:
            for one in ctx.message.mentions:
                name = re.sub(f'<@{one.id}>', one.name, name)
        if name is None:
            name = ctx.author.name
        pr_data = db["pr"].find_one({"name": {"$regex": "^{}$".format(name), "$options": "i"}})
        if pr_data:
            embed = discord.Embed(description=f"**{pr_data['name']}'s earnings:** {pr_data['earnings']}", colour=theme)
            await ctx.reply(embed=embed)
        else:
            embed = discord.Embed(description=f"**{name} is not power ranked**", colour=error_colour)
            await ctx.reply(embed=embed)

    @commands.hybrid_command(name='updatepr', with_app_command=True,
                             description=f'Updates the power ranking file', usage='')
    @app_commands.guilds(discord.Object(id=int(os.getenv('NSIG_SERVER'))))
    @commands.cooldown(1, 360, commands.BucketType.user)
    @commands.has_any_role(503631961185845269, 793387151148318720, 735685683716423691)
    async def updatepr(self, ctx):
        embed = discord.Embed(description=f'**PR file is being updated...**\n'
                                          f'Note that this command takes about a minute!', colour=argument_colour)
        msg = await ctx.reply(embed=embed)
        # Line below prevents blocking
        await self.bot.loop.run_in_executor(None, update_code)
        new_embed = discord.Embed(description=f'**PR file has been updated!**', colour=theme)
        await msg.edit(embed=new_embed)


def update_code():
    full_data_set = []
    i = 0
    regions = ["us-e", "eu", "sea", "brz", "aus"]
    game_modes = ["1v1", "2v2"]
    for single_region in regions:
        for game_mode in game_modes:
            page = requests.get(f"https://www.brawlhalla.com/rankings/power/{game_mode}/{single_region}")
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
                                social_one = social_one[:4] + 's' + social_one[4:]  # Adding character 's' to http
                            elif 'twitch.tv' in link["href"]:
                                social_two = link["href"]
                                social_two = social_two[:4] + 's' + social_two[4:]  # Adding character 's' to http
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

    for pr in full_data_set:
        cursor = db["stats"].aggregate([
            {
                "$match": {"$expr": {"$gte": [{"$size": {"$setIntersection": ["$socials", pr["socials"]]}}, 1]}}
            },
            {
                "$limit": 1
            }
        ])
        res = next(cursor, None)
        if res:
            pr["stats_id"] = res["id"]
        else:
            res = db["stats"].find_one({"name": {"$regex": "^{}$".format(pr["name"]), "$options": "i"}})
            if res:
                pr["stats_id"] = res["id"]

    db["pr"].delete_many({})
    db["pr"].insert_many(full_data_set)


async def setup(bot):
    await bot.add_cog(Pr(bot))
