import random

from pymongo import MongoClient
import os
from universal import *


# MongoDB information
cluster = MongoClient(os.getenv("MONGO_TOKEN"))
db = cluster["discord"]
collection = db["bracket"]


class AvatarButtons(discord.ui.View):
    def __init__(self, ctx, response, embeds):
        super().__init__(timeout=300)
        self.response = response
        self.ctx = ctx
        self.embeds = embeds
        self.page_number = 0

    async def on_timeout(self):
        self.clear_items()
        await self.response.edit(view=self)

    async def interaction_check(self, interaction) -> bool:
        if interaction.user != self.ctx.author:
            return False
        else:
            return True

    @discord.ui.button(label='Server', style=discord.ButtonStyle.green, custom_id='1', disabled=True)
    async def av_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        for one in self.children:
            if one.custom_id == '2':
                one.disabled = False
        button.disabled = True
        await interaction.response.edit_message(embed=self.embeds[0], view=self)

    @discord.ui.button(label='Global', style=discord.ButtonStyle.green, custom_id='2')
    async def av_2(self, interaction: discord.Interaction, button: discord.ui.Button):
        for one in self.children:
            if one.custom_id == '1':
                one.disabled = False
        button.disabled = True
        await interaction.response.edit_message(embed=self.embeds[1], view=self)


class Public(commands.Cog, name="Public"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.weapons = ["hammer", "sword", "blasters", "lance", "spear", "katars", "axe", "bow",
                        "gauntlets", "scythe", "cannon", "orb", "greatsword", "boots"]
        self.nsigs = {
        "ada": {"blasters": "https://cdn.discordapp.com/attachments/962692289237504012/962710314267345026/2022-04-10_08_41_36-Brawlhalla.png",
                "spear": "https://cdn.discordapp.com/attachments/962692289237504012/962710314510594088/2022-04-10_08_46_16-Brawlhalla.png"},
        "arcadia": {"spear": "https://cdn.discordapp.com/attachments/962692289237504012/962710314787426304/2022-04-10_08_52_26-Brawlhalla.png",
                    "greatsword": "https://cdn.discordapp.com/attachments/962692289237504012/962710315005526096/2022-04-10_08_55_11-Brawlhalla.png"},
        "artemis": {"lance": "https://cdn.discordapp.com/attachments/962692289237504012/962710315232026714/2022-04-10_08_55_48-Brawlhalla.png",
                    "scythe": "https://cdn.discordapp.com/attachments/962692289237504012/962710315458527232/2022-04-10_08_58_57-Brawlhalla.png"},
        "asuri": {"katars": "https://cdn.discordapp.com/attachments/962692289237504012/962710315697582080/2022-04-10_08_59_28-Brawlhalla.png",
                  "sword": "https://cdn.discordapp.com/attachments/962692289237504012/962710315924082698/2022-04-10_08_59_46-Brawlhalla.png"},
        "azoth": {"bow": "https://cdn.discordapp.com/attachments/962692289237504012/962710316158972004/2022-04-10_09_00_49-Brawlhalla.png",
                  "axe": "https://cdn.discordapp.com/attachments/962692289237504012/962710340209115146/2022-04-10_09_03_20-Brawlhalla.png"},
        "barraza": {"blasters": "https://cdn.discordapp.com/attachments/962692289237504012/962710340418822205/2022-04-10_09_04_04-Brawlhalla.png",
                    "axe": "https://cdn.discordapp.com/attachments/962692289237504012/962710340641112104/2022-04-10_09_04_25-Brawlhalla.png"},
        "brynn": {"axe": "https://cdn.discordapp.com/attachments/962692289237504012/962710340871790692/2022-04-10_09_05_01-Brawlhalla.png",
                  "spear": "https://cdn.discordapp.com/attachments/962692289237504012/962710341081526382/2022-04-10_09_05_27-Brawlhalla.png"},
        "bodvar": {"hammer": "https://cdn.discordapp.com/attachments/962692289237504012/962710341278662726/2022-04-10_09_05_51-Brawlhalla.png",
                   "sword": "https://cdn.discordapp.com/attachments/962692289237504012/962710341500928010/2022-04-10_09_06_19-Brawlhalla.png"},
        "caspian": {"gauntlets": "https://cdn.discordapp.com/attachments/962692289237504012/962710341710647347/2022-04-10_09_06_50-Brawlhalla.png",
                    "katars": "https://cdn.discordapp.com/attachments/962692289237504012/962710341928755210/2022-04-10_09_07_18-Brawlhalla.png"},
        "cassidy": {"blasters": "https://cdn.discordapp.com/attachments/962692289237504012/962710362011099146/2022-04-10_09_08_07-Brawlhalla.png",
                    "hammer": "https://cdn.discordapp.com/attachments/962692289237504012/962710362283720744/2022-04-10_09_08_26-Brawlhalla.png"},
        "cross": {"blasters": "https://cdn.discordapp.com/attachments/962692289237504012/962710362518618122/2022-04-10_09_08_53-Brawlhalla.png",
                  "gauntlets": "https://cdn.discordapp.com/attachments/962692289237504012/962710362757668874/2022-04-10_09_09_18-Brawlhalla.png"},
        "diana": {"bow": "https://cdn.discordapp.com/attachments/962692289237504012/962710363055468614/2022-04-10_09_09_42-Brawlhalla.png",
                  "blasters": "https://cdn.discordapp.com/attachments/962692289237504012/962710363269390376/2022-04-10_09_10_43-Brawlhalla.png"},
        "dusk": {"spear": "https://cdn.discordapp.com/attachments/962692289237504012/962710363474903072/2022-04-10_09_11_05-Brawlhalla.png",
                 "orb": "https://cdn.discordapp.com/attachments/962692289237504012/962710363718176868/2022-04-10_09_11_29-Brawlhalla.png"},
        "ember": {"katars": "https://cdn.discordapp.com/attachments/962692289237504012/962710364024344576/2022-04-10_09_11_52-Brawlhalla.png",
                  "bow": "https://cdn.discordapp.com/attachments/962692289237504012/962710384433823814/2022-04-10_09_12_07-Brawlhalla.png"},
        "ezio": {"orb": "https://cdn.discordapp.com/attachments/962692289237504012/1003007467380289637/nsig-orb_1.png",
                 "sword": "https://cdn.discordapp.com/attachments/962692289237504012/1003008088342806678/nsig-sword_1.png"},
        "fait": {"scythe": "https://cdn.discordapp.com/attachments/962692289237504012/962710384672907294/2022-04-10_09_12_21-Brawlhalla.png",
                 "orb": "https://cdn.discordapp.com/attachments/962692289237504012/962710384924561408/2022-04-10_09_12_40-Brawlhalla.png"},
        "gnash": {"hammer": "https://cdn.discordapp.com/attachments/962692289237504012/962710385146880061/2022-04-10_09_12_57-Brawlhalla.png",
                  "spear": "https://cdn.discordapp.com/attachments/962692289237504012/962710385364987954/2022-04-10_09_13_12-Brawlhalla.png"},
        "hattori": {"sword": "https://cdn.discordapp.com/attachments/962692289237504012/962710385578876968/2022-04-10_09_13_38-Brawlhalla.png",
                    "spear": "https://cdn.discordapp.com/attachments/962692289237504012/962710385822150666/2022-04-10_09_14_13-Brawlhalla.png"},
        "isaiah": {"cannon": "https://cdn.discordapp.com/attachments/962692289237504012/962710386107371580/2022-04-10_09_14_37-Brawlhalla.png",
                   "blasters": "https://cdn.discordapp.com/attachments/962692289237504012/962710386308702278/2022-04-10_09_15_04-Brawlhalla.png"},
        "jaeyun": {"sword": "https://cdn.discordapp.com/attachments/962692289237504012/962710408135856178/2022-04-10_09_15_38-Brawlhalla.png",
                   "greatsword": "https://cdn.discordapp.com/attachments/962692289237504012/962710408387498054/2022-04-10_09_16_06-Brawlhalla.png"},
        "jhala": {"axe": "https://cdn.discordapp.com/attachments/962692289237504012/962710408601419867/2022-04-10_09_16_42-Brawlhalla.png",
                  "sword": "https://cdn.discordapp.com/attachments/962692289237504012/962710408836309003/2022-04-10_09_17_03-Brawlhalla.png"},
        "jiro": {"scythe": "https://cdn.discordapp.com/attachments/962692289237504012/962710409041817620/2022-04-10_09_17_32-Brawlhalla.png",
                 "sword": "https://cdn.discordapp.com/attachments/962692289237504012/962710409268326430/2022-04-10_09_17_59-Brawlhalla.png"},
        "kaya": {"spear": "https://cdn.discordapp.com/attachments/962692289237504012/962710409465446400/2022-04-10_09_18_24-Brawlhalla.png",
                 "bow": "https://cdn.discordapp.com/attachments/962692289237504012/962710409712893992/2022-04-10_09_18_49-Brawlhalla.png"},
        "koji": {"bow": "https://cdn.discordapp.com/attachments/962692289237504012/962710409931022388/2022-04-10_09_19_27-Brawlhalla.png",
                 "sword": "https://cdn.discordapp.com/attachments/962692289237504012/962710437282062376/2022-04-10_09_20_22-Brawlhalla.png"},
        "kor": {"hammer": "https://cdn.discordapp.com/attachments/962692289237504012/962710437525348372/2022-04-10_09_20_42-Brawlhalla.png",
                "gauntlets": "https://cdn.discordapp.com/attachments/962692289237504012/962710437785387079/2022-04-10_09_20_58-Brawlhalla.png"},
        "lin fei": {"katars": "https://cdn.discordapp.com/attachments/962692289237504012/962710438003474552/2022-04-10_09_21_29-Brawlhalla.png",
                    "cannon": "https://cdn.discordapp.com/attachments/962692289237504012/962710438238359602/2022-04-10_09_21_47-Brawlhalla.png"},
        "lucien": {"katars": "https://cdn.discordapp.com/attachments/962692289237504012/962710438473248798/2022-04-10_09_22_10-Brawlhalla.png",
                   "blasters": "https://cdn.discordapp.com/attachments/962692289237504012/962710438691364874/2022-04-10_09_22_25-Brawlhalla.png"},
        "magyar": {"hammer": "https://cdn.discordapp.com/attachments/962692289237504012/962710438955610223/2022-04-10_09_22_39-Brawlhalla.png",
                   "greatsword": "https://cdn.discordapp.com/attachments/962692289237504012/962710439203045436/2022-04-10_09_22_54-Brawlhalla.png"},
        "mako": {"greatsword": "https://cdn.discordapp.com/attachments/962692289237504012/962710465572659270/2022-04-10_09_23_16-Brawlhalla.png",
                 "katars": "https://cdn.discordapp.com/attachments/962692289237504012/962710465786560532/2022-04-10_09_23_29-Brawlhalla.png"},
        "mirage": {"spear": "https://cdn.discordapp.com/attachments/962692289237504012/962710466029817916/2022-04-10_09_23_45-Brawlhalla.png",
                   "scythe": "https://cdn.discordapp.com/attachments/962692289237504012/962710466306637875/2022-04-10_09_24_07-Brawlhalla.png"},
        "mordex": {"gauntlets": "https://cdn.discordapp.com/attachments/962692289237504012/962710466596057139/2022-04-10_09_24_41-Brawlhalla.png",
                   "scythe": "https://cdn.discordapp.com/attachments/962692289237504012/962710466877091930/2022-04-10_09_25_06-Brawlhalla.png"},
        "munin": {"bow": "https://cdn.discordapp.com/attachments/962692289237504012/962710467195842590/2022-04-10_09_25_27-Brawlhalla.png",
                  "scythe": "https://cdn.discordapp.com/attachments/962692289237504012/962710467426541639/2022-04-10_09_25_42-Brawlhalla.png"},
        "queen nai": {"spear": "https://cdn.discordapp.com/attachments/962692289237504012/962710467736911932/2022-04-10_09_26_15-Brawlhalla.png",
                      "katars": "https://cdn.discordapp.com/attachments/962692289237504012/962710484392505374/2022-04-10_09_26_44-Brawlhalla.png"},
        "nix": {"scythe": "https://cdn.discordapp.com/attachments/962692289237504012/962710484631552001/2022-04-10_09_27_10-Brawlhalla.png",
                "blasters": "https://cdn.discordapp.com/attachments/962692289237504012/962710484912574594/2022-04-10_09_27_31-Brawlhalla.png"},
        "onyx": {"gauntlets": "https://cdn.discordapp.com/attachments/962692289237504012/962710485193601034/2022-04-10_09_27_52-Brawlhalla.png",
                 "cannon": "https://cdn.discordapp.com/attachments/962692289237504012/962710485453660180/2022-04-10_09_28_11-Brawlhalla.png"},
        "orion": {"spear": "https://cdn.discordapp.com/attachments/962692289237504012/962710485696925786/2022-04-10_09_28_34-Brawlhalla.png",
                  "lance": "https://cdn.discordapp.com/attachments/962692289237504012/962710485982117948/2022-04-10_09_28_55-Brawlhalla.png"},
        "petra": {"orb": "https://cdn.discordapp.com/attachments/962692289237504012/962710486581919844/2022-04-10_09_29_32-Brawlhalla.png",
                  "gauntlets": "https://cdn.discordapp.com/attachments/962692289237504012/962710486971973632/2022-04-10_09_29_44-Brawlhalla.png"},
        "ragnir": {"axe": "https://cdn.discordapp.com/attachments/962692289237504012/962710502977470504/2022-04-10_09_30_01-Brawlhalla.png",
                   "katars": "https://cdn.discordapp.com/attachments/962692289237504012/962710503208136704/2022-04-10_09_30_13-Brawlhalla.png"},
        "rayman": {"axe": "https://cdn.discordapp.com/attachments/962692289237504012/962710503430426724/2022-04-10_09_30_57-Brawlhalla.png",
                   "gauntlets": "https://cdn.discordapp.com/attachments/962692289237504012/962710503661125652/2022-04-10_09_31_21-Brawlhalla.png"},
        "reno": {"blasters": "https://cdn.discordapp.com/attachments/962692289237504012/962710503866650634/2022-04-10_09_31_54-Brawlhalla.png",
                 "orb": "https://cdn.discordapp.com/attachments/962692289237504012/962712547633549322/2022-04-10_09_55_38-Brawlhalla.png"},
        "sir roland": {"lance": "https://cdn.discordapp.com/attachments/962692289237504012/962710504109924352/2022-04-10_09_32_06-Brawlhalla.png",
                       "sword": "https://cdn.discordapp.com/attachments/962692289237504012/962710504332210196/2022-04-10_09_32_20-Brawlhalla.png"},
        "scarlet": {"hammer": "https://cdn.discordapp.com/attachments/962692289237504012/962710518592843796/2022-04-10_09_32_38-Brawlhalla.png",
                    "lance": "https://cdn.discordapp.com/attachments/962692289237504012/962710518894825612/2022-04-10_09_32_53-Brawlhalla.png"},
        "sentinel": {"katars": "https://cdn.discordapp.com/attachments/962692289237504012/962710537966321706/2022-04-10_09_33_14-Brawlhalla.png",
                     "hammer": "https://cdn.discordapp.com/attachments/962692289237504012/962710538171846656/2022-04-10_09_33_26-Brawlhalla.png"},
        "sidra": {"sword": "https://cdn.discordapp.com/attachments/962692289237504012/962710538440286228/2022-04-10_09_33_46-Brawlhalla.png",
                  "cannon": "https://cdn.discordapp.com/attachments/962692289237504012/962710538725502976/2022-04-10_09_34_13-Brawlhalla.png"},
        "teros": {"hammer": "https://cdn.discordapp.com/attachments/962692289237504012/962710538943627264/2022-04-10_09_34_28-Brawlhalla.png",
                  "axe": "https://cdn.discordapp.com/attachments/962692289237504012/962710539220439070/2022-04-10_09_34_46-Brawlhalla.png"},
        "tezca": {"gauntlets": "https://cdn.discordapp.com/attachments/962692289237504012/1054533588604952686/tezcagauntlets.png",
                  "boots": "https://cdn.discordapp.com/attachments/962692289237504012/1054533588902760528/tezcaboots.png"},
        "thatch": {"sword": "https://cdn.discordapp.com/attachments/962692289237504012/962710539581157386/2022-04-10_09_35_16-Brawlhalla.png",
                   "blasters": "https://cdn.discordapp.com/attachments/962692289237504012/962710539849576458/2022-04-10_09_35_32-Brawlhalla.png"},
        "thor": {"hammer": "https://cdn.discordapp.com/attachments/962692289237504012/962710540080275456/2022-04-10_09_35_43-Brawlhalla.png",
                 "orb": "https://cdn.discordapp.com/attachments/962692289237504012/962710560112246814/2022-04-10_09_35_55-Brawlhalla.png"},
        "ulgrim": {"axe": "https://cdn.discordapp.com/attachments/962692289237504012/962710560338743346/2022-04-10_09_36_23-Brawlhalla.png",
                   "lance": "https://cdn.discordapp.com/attachments/962692289237504012/962710560586211368/2022-04-10_09_36_35-Brawlhalla.png"},
        "val": {"gauntlets": "https://cdn.discordapp.com/attachments/962692289237504012/962710560766574592/2022-04-10_09_36_59-Brawlhalla.png",
                "sword": "https://cdn.discordapp.com/attachments/962692289237504012/962710561001463808/2022-04-10_09_37_12-Brawlhalla.png"},
        "vector": {"bow": "https://cdn.discordapp.com/attachments/962692289237504012/962710561227960320/2022-04-10_09_37_35-Brawlhalla.png",
                   "lance": "https://cdn.discordapp.com/attachments/962692289237504012/962710561479598160/2022-04-10_09_37_59-Brawlhalla.png"},
        "volkov": {"scythe": "https://cdn.discordapp.com/attachments/962692289237504012/962710561714487326/2022-04-10_09_38_37-Brawlhalla.png",
                   "axe": "https://cdn.discordapp.com/attachments/962692289237504012/962710561961959434/2022-04-10_09_38_57-Brawlhalla.png"},
        "lord vraxx": {"blasters": "https://cdn.discordapp.com/attachments/962692289237504012/962710599723270184/2022-04-10_09_39_17-Brawlhalla.png",
                       "lance": "https://cdn.discordapp.com/attachments/962692289237504012/962710600050430032/2022-04-10_09_39_31-Brawlhalla.png"},
        "wu shang": {"spear": "https://cdn.discordapp.com/attachments/962692289237504012/962710600281120808/2022-04-10_09_39_59-Brawlhalla.png",
                     "gauntlets": "https://cdn.discordapp.com/attachments/962692289237504012/962710600515985408/2022-04-10_09_40_15-Brawlhalla.png"},
        "xull": {"axe": "https://cdn.discordapp.com/attachments/962692289237504012/962710600952197150/2022-04-10_09_41_01-Brawlhalla.png",
                 "cannon": "https://cdn.discordapp.com/attachments/962692289237504012/962710601182896188/2022-04-10_09_41_26-Brawlhalla.png"},
        "yumiko": {"bow": "https://cdn.discordapp.com/attachments/962692289237504012/962710601438724126/2022-04-10_09_41_58-Brawlhalla.png",
                   "hammer": "https://cdn.discordapp.com/attachments/962692289237504012/962710601686200340/2022-04-10_09_42_38-Brawlhalla.png"},
        "zariel": {"bow": "https://cdn.discordapp.com/attachments/962692289237504012/962710601895923753/2022-04-10_09_42_53-Brawlhalla.png",
                   "gauntlets": "https://cdn.discordapp.com/attachments/962692289237504012/962710602168533092/2022-04-10_09_43_11-Brawlhalla.png"}
        }

    @commands.hybrid_command(name='whois', with_app_command=True, aliases=['info'],
                             description=f'Shows info of a user', usage='(user)')
    @app_commands.describe(user='The user to inspect')
    @app_commands.guilds(discord.Object(id=int(os.getenv('NSIG_SERVER'))))
    async def whois(self, ctx, user: discord.Member = None):
        member = user
        if member is None:
            member = ctx.author
        embed = discord.Embed(description=f'**ID:** `{member.id}`',
                              colour=theme, timestamp=datetime.now(tz))
        embed.set_thumbnail(url=member.display_avatar)
        embed.set_author(name=f'User Info - {member}', icon_url=member.display_avatar)
        embed.add_field(name='Account Created On:', value=f'<t:{int(member.created_at.timestamp())}:D>')
        embed.add_field(name='Joined Server On:', value=f'<t:{int(member.joined_at.timestamp())}:D>')
        if len(member.roles[1:]) == 0:
            embed.add_field(name=f'Roles [{len(member.roles[1:])}]:', value=f'No roles')
        else:
            embed.add_field(name=f'Roles [{len(member.roles[1:])}]:',
                            value=", ".join([role.mention for role in member.roles[1:]]), inline=False)
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name='av', with_app_command=True, aliases=['avatar'],
                             description=f'Shows avatar of a user', usage='(user)')
    @app_commands.describe(user='The user to inspect')
    @app_commands.guilds(discord.Object(id=int(os.getenv('NSIG_SERVER'))))
    async def av(self, ctx, user: discord.Member = None):
        member = user
        if member is None:
            member = ctx.author
        if member.avatar.url != member.display_avatar.url:
            embed_server = discord.Embed(colour=theme)
            embed_server.set_image(url=member.display_avatar.url)
            embed_server.set_author(name=f"{member}'s server avatar:")

            embed_global = discord.Embed(colour=theme)
            embed_global.set_image(url=member.avatar.url)
            embed_global.set_author(name=f"{member}'s global avatar:")

            embed = discord.Embed(timestamp=datetime.now(tz), description=f'**Loading...**',
                                  colour=theme)
            msg = await ctx.reply(embed=embed)
            await msg.edit(embed=embed_server, view=AvatarButtons(embeds=[embed_server, embed_global], ctx=ctx,
                                                                  response=msg))
        else:
            embed = discord.Embed(colour=theme)
            embed.set_image(url=member.display_avatar.url)
            embed.set_author(name=f"{member}'s avatar:")
            await ctx.reply(embed=embed)

    @commands.hybrid_command(name='bracket', with_app_command=True,
                             description=f'Sends the bracket link', usage='')
    @app_commands.guilds(discord.Object(id=int(os.getenv('NSIG_SERVER'))))
    async def bracket(self, ctx):
        cur = collection.find({"_id": "bracket"})
        for one in cur:
            bracket = one['bracket']
        if bracket == "":
            embed = discord.Embed(description=f'**No bracket link set**', colour=error_colour)
            await ctx.reply(embed=embed)
        else:
            await ctx.reply(f'{bracket}')

    @commands.hybrid_command(name='nsig', with_app_command=True,
                             description=f'Displays an nSig', usage='(legend) (weapon)')
    @app_commands.describe(legend='The name of the legend')
    @app_commands.describe(weapon='The name of the weapon')
    @app_commands.guilds(discord.Object(id=int(os.getenv('NSIG_SERVER'))))
    @commands.has_any_role(873601521953148938, 586018286395719701, 793387151148318720,
                           735685683716423691, 503631961185845269)
    async def nsig(self, ctx, legend=None, weapon=None):
        # Swapping legend and weapon (arguments entered)
        if legend is not None:
            if legend.lower() in self.weapons:
                x = legend
                y = weapon
                weapon = x
                legend = y

        if legend is None:
            if weapon is None:
                character = random.choice(list(self.nsigs))
                weapon = random.choice(list(self.nsigs[character]))
                image_url = self.nsigs[character][weapon]
                embed = discord.Embed(title=f'Random nSig:', timestamp=datetime.now(tz), colour=theme)
                embed.set_image(url=f'{image_url}')
                await ctx.reply(embed=embed)
            elif weapon is not None:
                weapon = weapon.lower()
                if weapon not in self.weapons:
                    embed = discord.Embed(description=f'**Legend or weapon not found**', colour=error_colour)
                    await ctx.reply(embed=embed)
                    return
                invalid = True
                while invalid:
                    character = random.choice(list(self.nsigs))
                    try:
                        image_url = self.nsigs[character][weapon]
                        invalid = False
                    except KeyError:
                        pass
                embed = discord.Embed(title=f'Random {weapon.title()} nSig:', timestamp=datetime.now(tz), colour=theme)
                embed.set_image(url=f'{image_url}')
                await ctx.reply(embed=embed)
        elif legend is not None:
            if weapon is None:
                character = legend.lower()
                if character not in self.nsigs:
                    embed = discord.Embed(description=f'**Legend or weapon not found**', colour=error_colour)
                    await ctx.reply(embed=embed)
                    return
                weapon = random.choice(list(self.nsigs[character]))
                image_url = self.nsigs[character][weapon]
                embed = discord.Embed(title=f'Random {character.title()} nSig:', timestamp=datetime.now(tz),
                                      colour=discord.Colour.green())
                embed.set_image(url=f'{image_url}')
                await ctx.reply(embed=embed)
            elif weapon is not None:
                character = legend.lower()
                if character not in self.nsigs:
                    embed = discord.Embed(description=f'**Legend or weapon not found**', colour=error_colour)
                    await ctx.reply(embed=embed)
                    return
                weapon = weapon.lower()
                if weapon not in self.nsigs[character]:
                    embed = discord.Embed(description=f'**Legend or weapon not found**', colour=error_colour)
                    await ctx.reply(embed=embed)
                    return
                image_url = self.nsigs[character][weapon]
                if weapon.endswith("s"):
                    weapon = weapon[:-1]
                embed = discord.Embed(title=f'{character.title()} {weapon.title()} nSig:', timestamp=datetime.now(tz),
                                      colour=theme)
                embed.set_image(url=f'{image_url}')
                await ctx.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(Public(bot))
