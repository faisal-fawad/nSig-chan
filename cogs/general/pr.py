from bs4 import BeautifulSoup
import requests
import orjson as json
import re
from pymongo import MongoClient
import os
from universal import *


cluster = MongoClient(os.getenv("MONGO_TOKEN"))
db = cluster["website"]


async def create_pr_embed(full_data, mode_data, info_data, mode):
    # Data from full result
    name = full_data["player"]["name"]
    region = full_data["region"]
    if region is None:
        region = "N/A"
    try:
        twitter = "https://twitter.com/" + info_data["player"]["twitter"]
    except KeyError:
        twitter = None
    try:
        twitch = "https://www.twitch.tv/" + info_data["player"]["twitch"]
    except KeyError:
        twitch = None

    # Data from mode result
    rank = mode_data["pr"]["powerRanking"]
    if rank == 0:
        rank = full_data[f"pr{mode}"]
        if rank is None:
            rank = "N/A"
    money_made = mode_data["earnings"]
    top_8 = mode_data["pr"]["top8"]
    top_32 = mode_data["pr"]["top32"]
    gold = mode_data["pr"]["gold"]
    silver = mode_data["pr"]["silver"]
    bronze = mode_data["pr"]["bronze"]

    full_embed = discord.Embed(colour=discord.Colour.green(), title=f'Statistics for {name}',
                               timestamp=datetime.now(tz),
                               description=f'**PR:** {rank} \n'
                                           f'**Region:** {region.upper()} \n'
                                           f'**Mode:** {mode}')
    full_embed.add_field(name=f'Placements:', value=f'**Earnings:** ${money_made} \n'
                                                    f'**Top 8:** {top_8} \n'
                                                    f'**Top 32:** {top_32}', inline=True)
    full_embed.add_field(name=f'Medals:', value=f'**Gold:** 🥇 {gold} \n'
                                                f'**Silver:** 🥈 {silver} \n'
                                                f'**Bronze:** 🥉 {bronze}', inline=True)
    full_embed.add_field(name=f'Socials:', value=f'**Twitter:** {twitter} \n'
                                                 f'**Twitch:** {twitch}', inline=False)
    return full_embed


async def create_stats_embed(tournaments, name):
    def make_ordinal(n):
        n = int(n)
        if 11 <= (n % 100) <= 13:
            suffix = 'th'
        else:
            suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
        return str(n) + suffix

    pages = []
    split_tournaments = [tournaments[x:x + 5] for x in range(0, len(tournaments), 5)]
    for number, section in enumerate(split_tournaments):
        full_description = f''
        for tournament in section:
            time = datetime.utcfromtimestamp(tournament["tournament"]["startTime"]).strftime('%m/%d/%Y')
            tournament_string = f'**[{tournament["tournament"]["tournamentName"]}]({"https://www.start.gg/" + tournament["tournament"]["slug"]})** \n' \
                                f'**Date:** {time} \n' \
                                f'**Placement:** {make_ordinal(tournament["placement"])} \n\n' \

            full_description = full_description + tournament_string
        full_embed = discord.Embed(colour=theme, title=f'Tournament history for {name}',
                                   timestamp=datetime.now(tz), description=full_description)
        full_embed.set_footer(text=f"Page {number + 1}/{len(split_tournaments)}")
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
            self.page_number = self.max_page
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
                    one.disabled = False
                if one.custom_id == '5':
                    one.disabled = False
        button.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label='>>', style=discord.ButtonStyle.green, custom_id='5', disabled=True)
    async def power_5(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page_number = self.page_number + 1
        if self.page_number > self.max_page:
            self.page_number = 0
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
        
        if name.count(" ") != 0:
            embed = discord.Embed(timestamp=datetime.now(tz), description=f"**Spaces not supported**",
                                  colour=error_colour)
            await msg.edit(embed=embed)
            return

        # Sending request to server
        req = requests.post("https://api.brawltools.com/player/search", json={"query": name})
        try: 
            res = req.json()["searchPlayers"][0]
            id = res["player"]["smashId"]
        except (KeyError, IndexError):
            embed = discord.Embed(timestamp=datetime.now(tz), description=f'**{name} is not power ranked**',
                                  colour=error_colour)
            await msg.edit(embed=embed)
            return

        # Grabbing PR in game modes and updated info (Code should not error past this point)
        req = requests.post("https://api.brawltools.com/player/pr", json={"entrantSmashIds": [id], "gameMode": 1})
        res_1v1 = req.json()

        req = requests.post("https://api.brawltools.com/player/pr", json={"entrantSmashIds": [id], "gameMode": 2})
        res_2v2 = req.json()

        req = requests.get(f"https://api.brawltools.com/player/{id}")
        res_info = req.json()

        res_stats = []
        # Grabs both 1V1 and 2V2 stats
        for i in range(1, 3):
            req = requests.post("https://api.brawltools.com/player/placement", json={"entrantSmashIds": [id], "gameMode": i, "isOfficial": True})
            res_stats.extend(req.json()["playerPlacements"])
            while req.json()["nextToken"]:
                req = requests.post("https://api.brawltools.com/player/placement", json={"entrantSmashIds": [id], "gameMode": i, "isOfficial": True, "nextToken": req.json()["nextToken"]})
                res_stats.extend(req.json()["playerPlacements"])
        
        # Creating embeds via function
        power_1v1 = await create_pr_embed(res, res_1v1, res_info, "1v1")    
        power_2v2 = await create_pr_embed(res, res_2v2, res_info, "2v2")
        stats = await create_stats_embed(res_stats, res["player"]["name"])

        await msg.edit(embed=power_1v1, view=PowerButtons(embeds=[power_1v1, power_2v2], pages=stats,
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

        if name.count(" ") != 0:
            embed = discord.Embed(timestamp=datetime.now(tz), description=f"**Spaces not supported**",
                                  colour=error_colour)
            await ctx.reply(embed=embed)
            return
        
        # Sending request to server
        req = requests.post("https://api.brawltools.com/player/search", json={"query": name})
        try: 
            res = req.json()["searchPlayers"][0]
            id = res["player"]["smashId"]
        except (KeyError, IndexError):
            embed = discord.Embed(timestamp=datetime.now(tz), description=f'**{name} is not power ranked**',
                                  colour=error_colour)
            await ctx.reply(embed=embed)
            return
        
        req = requests.post("https://api.brawltools.com/player/pr", json={"entrantSmashIds": [id], "gameMode": 1})
        embed = discord.Embed(description=f"**{res['player']['name']}'s earnings:** ${req.json()['earnings']}", colour=theme)
        await ctx.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(Pr(bot))
