import discord.app_commands

from universal import *
import os


class Admin(commands.Cog, name="Admin"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name='load', with_app_command=True, aliases=['add'],
                             description=f'Adds an extension', usage='[folder] [file]')
    @app_commands.describe(folder='The name of the folder')
    @app_commands.describe(file='The name of the file')
    @app_commands.guilds(discord.Object(id=int(os.getenv('NSIG_SERVER'))))
    @commands.is_owner()
    async def load(self, ctx, folder, file):
        await self.bot.load_extension(f'cogs.{folder}.{file}')
        embed = discord.Embed(description=f'**Extension loaded**', colour=theme)
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name='unload', with_app_command=True, aliases=['remove'],
                             description=f'Removes an extension', usage='[folder] [file]')
    @app_commands.describe(folder='The name of the folder')
    @app_commands.describe(file='The name of the file')
    @app_commands.guilds(discord.Object(id=int(os.getenv('NSIG_SERVER'))))
    @commands.is_owner()
    async def unload(self, ctx, folder, file):
        await self.bot.unload_extension(f'cogs.{folder}.{file}')
        embed = discord.Embed(description=f'**Extension unloaded**', colour=theme)
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name='reload', with_app_command=True, aliases=['update'],
                             description=f'Reloads an extension', usage='[folder] [file]')
    @app_commands.describe(folder='The name of the folder')
    @app_commands.describe(file='The name of the file')
    @app_commands.guilds(discord.Object(id=int(os.getenv('NSIG_SERVER'))))
    @commands.is_owner()
    async def reload(self, ctx, folder, file):
        await self.bot.reload_extension(f'cogs.{folder}.{file}')
        embed = discord.Embed(description=f'**Extension reloaded**', colour=theme)
        await ctx.reply(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Admin(bot))
