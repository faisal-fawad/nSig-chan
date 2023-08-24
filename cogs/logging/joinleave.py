import os
import pymongo.errors
import asyncio
from pymongo import MongoClient
from universal import *

# MongoDB information
cluster = MongoClient(os.getenv("MONGO_TOKEN"))
db = cluster["discord"]
collection = db["users"]


class JoinLeave(commands.Cog, name="JoinLeave"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = self.bot.get_channel(int(os.getenv('JOIN_LOGS')))
        embed = discord.Embed(colour=theme, timestamp=datetime.now(tz))
        embed.set_author(name=f'{member} has joined', icon_url=member.display_avatar)
        embed.add_field(name='Account Created On:', value=f'<t:{int(member.created_at.timestamp())}:f>', inline=False)
        embed.set_footer(text=f'ID: {member.id}')
        embed.set_thumbnail(url=member.display_avatar)
        await channel.send(embed=embed)
        main_role = discord.utils.get(member.guild.roles, id=int(os.getenv('WELCOME_ROLE')))
        results = collection.find_one({"_id": member.id})
        if results is not None:
            muted_role = discord.utils.get(member.guild.roles, id=int(os.getenv('UNLUCKY_ROLE')))
            await member.add_roles(muted_role)
            collection.delete_one({"_id": member.id})
        if results is None:
            pass
        await asyncio.sleep(300)
        try:
            await member.add_roles(main_role)
        except discord.NotFound:
            pass

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        channel = self.bot.get_channel(int(os.getenv('JOIN_LOGS')))
        embed = discord.Embed(colour=error_colour, timestamp=datetime.now(tz))
        embed.set_author(name=f'{member} has left', icon_url=member.display_avatar)
        embed.set_footer(text=f'ID: {member.id}')
        if len(member.roles[1:]) == 0:
            embed.add_field(name=f'Roles [{len(member.roles[1:])}]:', value=f'No roles')
        else:
            embed.add_field(name=f'Roles [{len(member.roles[1:])}]:',
                            value=", ".join([role.mention for role in member.roles[1:]]))
        await channel.send(embed=embed)
        for role in member.roles:
            try:
                if role.id == int(os.getenv('UNLUCKY_ROLE')):
                    post = {"_id": member.id}
                    collection.insert_one(post)
            except pymongo.errors.DuplicateKeyError:
                pass


async def setup(bot) -> None:
    await bot.add_cog(JoinLeave(bot))
