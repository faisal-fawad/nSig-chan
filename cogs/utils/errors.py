import os
from universal import *


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return

        ignored = (commands.CommandNotFound, )
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            pass

        elif isinstance(error, commands.CommandNotFound):
            pass

        elif isinstance(error, commands.MissingPermissions):
            if ctx.interaction is not None:
                embed = discord.Embed(description=f'**You do not have permission to run this command**',
                                      colour=error_colour)
                await ctx.reply(embed=embed, ephemeral=True)

        elif isinstance(error, commands.MissingAnyRole):
            if ctx.interaction is not None:
                embed = discord.Embed(description=f'**You do not have permission to run this command**',
                                      colour=error_colour)
                await ctx.reply(embed=embed, ephemeral=True)

        elif isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(description=f'**Member not found**', colour=error_colour)
            await ctx.reply(embed=embed)

        elif isinstance(error, commands.RoleNotFound):
            embed = discord.Embed(description=f'**Role not found**', colour=error_colour)
            await ctx.reply(embed=embed)

        elif isinstance(error, commands.ChannelNotFound):
            embed = discord.Embed(description=f'**Channel not found**', colour=error_colour)
            await ctx.reply(embed=embed)

        elif isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(description="**Command on cooldown, try again in {:.1f}s**".format(error.retry_after),
                                  colour=error_colour)
            await ctx.reply(embed=embed)

        elif isinstance(error, commands.ExtensionNotFound):
            embed = discord.Embed(description="**Extension not found**",
                                  colour=error_colour)
            await ctx.reply(embed=embed)

        elif isinstance(error, commands.ExtensionAlreadyLoaded):
            embed = discord.Embed(description="**Extension already loaded**",
                                  colour=error_colour)
            await ctx.reply(embed=embed)

        elif isinstance(error, commands.ExtensionNotLoaded):
            embed = discord.Embed(description="**Extension could not be loaded**",
                                  colour=error_colour)
            await ctx.reply(embed=embed)

        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(description=f'**Missing required argument** \n'
                                              f'View arguments by typing: `{os.getenv("BOT_PREFIX")}help '
                                              f'{ctx.command.name}`',
                                  colour=error_colour)
            await ctx.reply(embed=embed)

        elif isinstance(error, discord.errors.Forbidden):
            embed = discord.Embed(description=f'**nSig-chan is missing permissions**',
                                  colour=error_colour)
            await ctx.reply(embed=embed)

        elif isinstance(error, commands.NoPrivateMessage):
            embed = discord.Embed(description=f'**This command is not supported in DMs**',
                                  colour=error_colour)
            await ctx.reply(embed=embed)

        elif isinstance(error, commands.UnexpectedQuoteError):
            embed = discord.Embed(description=f'**Parsing error**',
                                  colour=error_colour)
            await ctx.reply(embed=embed)

        elif isinstance(error, discord.errors.HTTPException):
            print('HTTP Exception')
            print(f'Error Code: {error}')

        else:
            raise error


async def setup(bot) -> None:
    await bot.add_cog(ErrorHandler(bot))
