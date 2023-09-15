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
    @app_commands.describe(roles='The roles that will be given; Seperate roles with a comma')
    @app_commands.describe(user='The user to give the role to')
    @app_commands.guilds(discord.Object(id=int(os.getenv('NSIG_SERVER'))))
    @commands.has_permissions(manage_roles=True)
    async def give(self, ctx, user: discord.Member, *, roles):
        embed = discord.Embed(timestamp=datetime.now(tz), description=f'**Loading...**',
                              colour=theme)
        msg = await ctx.reply(embed=embed)
        member = user
        new_roles = []
        errors = {"Roles: {} not found": [], "Roles: {} are above you": [], "User already has roles: {}": []}
        roles = [role.strip() for role in roles.split(",")]
        for role in roles:
            cur = discord.utils.get(ctx.guild.roles, name=role)
            if cur is None:
                try:
                    cur = role.replace("<@&", "").replace(">", "")
                    cur = ctx.guild.get_role(int(cur))
                except ValueError: # Unable to convert cur to integer
                    cur = None
            if cur is not None:
                role = cur
                if role not in new_roles: # Cannot be duplicate role
                    if role not in member.roles:
                        if role < ctx.author.top_role or self.bot.owner_id == ctx.author.id:
                            new_roles.append(role)
                        else:
                            errors["Roles: {} are above you"].append(f"{role.mention}")
                    else:
                        errors["User already has roles: {}"].append(f"{role.mention}")
            else:
                errors["Roles: {} not found"].append(f"{role}")
        # Creating error message
        error_msg = ""
        for error in errors:
            if len(errors[error]) != 0:
                error_msg += error.format(", ".join(errors[error])) + "\n"
        if error_msg:
            error_msg = "**Ran into the following errors: **\n" + error_msg
        
        # Series of checks
        if len(new_roles) == 0:
            embed = discord.Embed(description=error_msg, colour=error_colour)
            await msg.edit(embed=embed)
            return
        elif self.bot.owner_id == ctx.author.id:
            pass
        elif member.id == ctx.author.id:
            pass
        elif member.top_role >= ctx.author.top_role:
            embed = discord.Embed(description=f'**You can only moderate members below your role**', colour=error_colour)
            await msg.edit(embed=embed)
            return
        await member.add_roles(*new_roles)
        embed = discord.Embed(description=f'**{member} received {", ".join([role.mention for role in new_roles])}**\n\n' + error_msg, colour=theme)
        await msg.edit(embed=embed)

    @commands.hybrid_command(name='take', with_app_command=True,
                             description=f'Takes a role from a user', usage='[user] [role]')
    @app_commands.describe(roles='The roles that will be taken; Seperate roles with a comma')
    @app_commands.describe(user='The user to take the role from')
    @app_commands.guilds(discord.Object(id=int(os.getenv('NSIG_SERVER'))))
    @commands.has_permissions(manage_roles=True)
    async def take(self, ctx, user: discord.Member, *, roles):
        embed = discord.Embed(timestamp=datetime.now(tz), description=f'**Loading...**',
                              colour=theme)
        msg = await ctx.reply(embed=embed)
        member = user
        new_roles = []
        errors = {"Roles: {} not found": [], "Roles: {} are above you": [], "User doesn't have roles: {}": []}
        roles = [role.strip() for role in roles.split(",")]
        for role in roles:
            cur = discord.utils.get(ctx.guild.roles, name=role)
            if cur is None:
                try:
                    cur = role.replace("<@&", "").replace(">", "")
                    cur = ctx.guild.get_role(int(cur))
                except ValueError: # Unable to convert cur to integer
                    cur = None
            if cur is not None:
                role = cur
                if role not in new_roles: # Cannot be duplicate role
                    if role in member.roles:
                        if role < ctx.author.top_role or self.bot.owner_id == ctx.author.id:
                            new_roles.append(role)
                        else:
                            errors["Roles: {} are above you"].append(f"{role.mention}")
                    else:
                        errors["User doesn't have roles: {}"].append(f"{role.mention}")
            else:
                errors["Roles: {} not found"].append(f"{role}")
        # Creating error message
        error_msg = ""
        for error in errors:
            if len(errors[error]) != 0:
                error_msg += error.format(", ".join(errors[error])) + "\n"
        if error_msg:
            error_msg = "**Ran into the following errors: **\n" + error_msg

        # Series of checks
        if len(new_roles) == 0:
            embed = discord.Embed(description=error_msg, colour=error_colour)
            await msg.edit(embed=embed)
            return
        elif self.bot.owner_id == ctx.author.id:
            pass
        elif member.id == ctx.author.id:
            pass
        elif member.top_role >= ctx.author.top_role:
            embed = discord.Embed(description=f'**You can only moderate members below your role**', colour=error_colour)
            await msg.edit(embed=embed)
            return
        await member.remove_roles(*new_roles)
        embed = discord.Embed(description=f'**{member} lost {", ".join([role.mention for role in new_roles])}**\n\n' + error_msg, colour=theme)
        await msg.edit(embed=embed)


async def setup(bot) -> None:
    await bot.add_cog(Roles(bot))
