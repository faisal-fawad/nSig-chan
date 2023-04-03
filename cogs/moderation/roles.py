from universal import *
import os


class Roles(commands.Cog, name="Roles"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name='color', with_app_command=True, aliases=['colour'],
                             description=f'Changes the color of a role', usage='[hex] [role]')
    @app_commands.describe(role='The role to change')
    @app_commands.describe(color='The color to change the role to; Must be a hex code')
    @app_commands.guilds(discord.Object(id=int(os.getenv('NSIG_SERVER'))))
    @commands.has_permissions(manage_roles=True)
    async def color(self, ctx, color, *, role: discord.Role):
        colour_code = color
        search = '#'
        if search in colour_code:
            colour_code = colour_code.replace('#', '')
        try:
            colour_code = (int(colour_code, 16))
        except ValueError:
            embed = discord.Embed(description=f'**The hex was entered incorrectly** \n'
                                              f'eg) #F82A12, 8161AD', colour=error_colour)
            await ctx.reply(embed=embed)
            return
        lower_role = role.name.lower()
        if lower_role == role:
            await role.edit(colour=colour_code)
            embed = discord.Embed(description=f"**Updated {role.mention}'s color**", colour=theme)
            await ctx.reply(embed=embed)
        else:
            await role.edit(colour=colour_code)
            embed = discord.Embed(description=f"**Updated {role.mention}'s color**", colour=theme)
            await ctx.reply(embed=embed)

    @commands.hybrid_command(name='give', with_app_command=True,
                             description=f'Gives a role to a user', usage='[user] [role]')
    @app_commands.describe(role='The role that will be given')
    @app_commands.describe(user='The user to give the role to')
    @app_commands.guilds(discord.Object(id=int(os.getenv('NSIG_SERVER'))))
    @commands.has_permissions(manage_roles=True)
    async def give(self, ctx, user: discord.Member, *, role: discord.Role):
        member = user
        if role in member.roles:
            embed = discord.Embed(description=f'**User already has that role**', colour=error_colour)
            await ctx.reply(embed=embed)
            return
        elif self.bot.owner_id == ctx.author.id:
            pass
        elif role >= ctx.author.top_role:
            embed = discord.Embed(description=f'**You can only give roles below you**', colour=error_colour)
            await ctx.reply(embed=embed)
            return
        elif member.id == ctx.author.id:
            pass
        elif member.top_role >= ctx.author.top_role:
            embed = discord.Embed(description=f'**You can only moderate members below your role**', colour=error_colour)
            await ctx.reply(embed=embed)
            return
        await member.add_roles(role)
        embed = discord.Embed(description=f'**{member} received {role.mention}**', colour=theme)
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name='take', with_app_command=True,
                             description=f'Takes a role from a user', usage='[user] [role]')
    @app_commands.describe(role='The role that will be taken')
    @app_commands.describe(user='The user to take the role from')
    @app_commands.guilds(discord.Object(id=int(os.getenv('NSIG_SERVER'))))
    @commands.has_permissions(manage_roles=True)
    async def take(self, ctx, user: discord.Member, *, role: discord.Role):
        member = user
        if role not in member.roles:
            embed = discord.Embed(description=f'**User does not have that role**', colour=error_colour)
            await ctx.reply(embed=embed)
            return
        elif self.bot.owner_id == ctx.author.id:
            pass
        elif member.id == ctx.author.id:
            if role == member.top_role:
                embed = discord.Embed(description=f'**You cannot take your top role**', colour=error_colour)
                await ctx.reply(embed=embed)
                return
            else:
                pass
        elif member.top_role >= ctx.author.top_role:
            embed = discord.Embed(description=f'**You can only moderate members below your role**', colour=error_colour)
            await ctx.reply(embed=embed)
            return
        await member.remove_roles(role)
        embed = discord.Embed(description=f'**{member} lost {role.mention}**', colour=theme)
        await ctx.reply(embed=embed)


async def setup(bot) -> None:
    await bot.add_cog(Roles(bot))
