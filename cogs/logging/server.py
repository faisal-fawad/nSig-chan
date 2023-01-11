import os
from universal import *


class Server(commands.Cog, name="Server"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        channel = self.bot.get_channel(int(os.getenv('SERVER_LOGS')))
        embed = discord.Embed(description=f'**Name:** {role.name}', colour=role.color,
                              timestamp=datetime.now(tz))
        embed.set_author(name=f'nSig - Role Created',
                         icon_url=role.guild.icon)
        embed.set_footer(text=f'ID: {role.id}')
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        channel = self.bot.get_channel(int(os.getenv('SERVER_LOGS')))
        embed = discord.Embed(description=f'**Name:** {role.name}', colour=role.color,
                              timestamp=datetime.now(tz))
        embed.set_author(name=f'nSig - Role Deleted',
                         icon_url=role.guild.icon)
        embed.set_footer(text=f'ID: {role.id}')
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        channel = self.bot.get_channel(int(os.getenv('SERVER_LOGS')))
        if before.name != after.name and before.color != after.color:
            embed = discord.Embed(colour=after.color, timestamp=datetime.now(tz),
                                  description=f'**Before:** {before.name}, {before.color} \n'
                                              f'**After:** {after.name}, {after.color}')
            embed.set_author(name=f'nSig - Role Name/Color Changed',
                             icon_url=before.guild.icon)
            embed.set_footer(text=f'ID: {before.id}')
        elif before.name != after.name:
            embed = discord.Embed(colour=after.color, timestamp=datetime.now(tz),
                                  description=f'**Before:** {before.name} \n'
                                              f'**After:** {after.name}')
            embed.set_author(name=f'nSig - Role Name Changed',
                             icon_url=before.guild.icon)
            embed.set_footer(text=f'ID: {before.id}')
        elif before.color != after.color:
            embed = discord.Embed(colour=after.color, timestamp=datetime.now(tz),
                                  description=f'**Name:** {before.name} \n'
                                              f'**Before:** {before.color} \n'
                                              f'**After:** {after.color}')
            embed.set_author(name=f'nSig - Role Color Changed',
                             icon_url=before.guild.icon)
            embed.set_footer(text=f'ID: {before.id}')
        else:
            return
        await channel.send(embed=embed)


async def setup(bot) -> None:
    await bot.add_cog(Server(bot))
