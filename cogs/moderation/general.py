import os
import asyncio
import re
from universal import *


async def kick_func(ctx, user, reason):
    try:
        await user.send(f'You have been kicked from nSig for: \n'
                        f'{reason}')
    except (discord.Forbidden, discord.HTTPException):
        pass
    await user.kick(reason=reason)
    embed = discord.Embed(description=f'**{user} has been kicked from nSig**',
                          colour=theme)
    await ctx.reply(embed=embed)


async def ban_func(ctx, user, reason, ban_normal):
    if ban_normal is True:
        try:
            await user.send(f'You have been banned from nSig for: \n'
                            f'{reason}')
        except (discord.Forbidden, discord.HTTPException):
            pass
        await user.ban(reason=reason, delete_message_days=1)
    else:
        await ctx.guild.ban(discord.Object(id=user.id))
    embed = discord.Embed(description=f'**{user} has been banned from nSig**',
                          colour=theme)
    await ctx.reply(embed=embed)


async def mute_func(self, ctx, member, time, reason):
    muted_role = discord.utils.get(ctx.guild.roles, id=int(os.getenv('UNLUCKY_ROLE')))
    time_convert = {"s": 1, "m": 60, "h": 3600, "hr": 3600, "d": 86400, "w": 604800}
    if time is None:
        time = "1hr"
        temp_mute = 3600
        if reason is None:
            reason = "No reason provided"
    elif time is not None:
        try:
            split_time = re.findall('(\d+|[A-Za-z]+)', time)
            temp_mute = int(split_time[0]) * int(time_convert[split_time[1]])
            if reason is None:
                reason = "No reason provided"
        except (TypeError, ValueError, KeyError):
            if reason is None:
                reason = f'{time}'
            else:
                reason = f'{time} {reason}'
            temp_mute = 3600
            time = "1hr"
    if int(temp_mute) == 0:
        embed = discord.Embed(description='**The duration entered was zero**', colour=error_colour)
        await ctx.reply(embed=embed)
        return
    await member.add_roles(muted_role)
    embed = discord.Embed(description=f'**{member} has been muted**', colour=theme)
    await ctx.reply(embed=embed)
    self.bot.dispatch('mute', ctx, member, time, reason)
    try:
        await member.send(f'You have been muted in nSig for **{time}** \n'
                          f'**Reason:** {reason}')
    except (discord.HTTPException, discord.Forbidden):
        pass
    await asyncio.sleep(temp_mute)
    if muted_role not in member.roles:
        pass
    else:
        self.bot.dispatch('unmute', ctx, member, f'{self.bot.user.mention}')
        await member.remove_roles(muted_role)


class Moderation(commands.Cog, name="Moderation"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name='kick', with_app_command=True, aliases=['k'],
                             description=f'Kicks a user from the server', usage='[member] (reason)')
    @app_commands.describe(user='The user to kick')
    @app_commands.describe(reason='The reason for kicking the user')
    @app_commands.guilds(discord.Object(id=int(os.getenv('NSIG_SERVER'))))
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member, *, reason="No reason provided"):
        if user.id == self.bot.user.id:
            embed = discord.Embed(description=f'**You cannot kick the bot**', colour=error_colour)
            await ctx.reply(embed=embed)
        elif user.id == ctx.author.id:
            embed = discord.Embed(description=f'**You cannot kick yourself**', colour=error_colour)
            await ctx.reply(embed=embed)
        elif user.id == ctx.guild.owner.id:
            embed = discord.Embed(description=f'**You cannot kick the owner of the server**', colour=error_colour)
            await ctx.reply(embed=embed)
        elif ctx.author.id == ctx.guild.owner.id:
            await kick_func(ctx, user, reason)
            self.bot.dispatch('kick', ctx, user, reason)
        elif user.top_role >= ctx.author.top_role:  # checks if moderator is above target
            embed = discord.Embed(description=f'**You can only moderate members below your role**', colour=error_colour)
            await ctx.reply(embed=embed)
        else:
            await kick_func(ctx, user, reason)
            self.bot.dispatch('kick', ctx, user, reason)

    @commands.hybrid_command(name='ban', with_app_command=True, aliases=['b'],
                             description=f'Bans a user from the server', usage='[user] (reason)')
    @app_commands.describe(user='The user to ban')
    @app_commands.describe(reason='The reason for banning the user')
    @app_commands.guilds(discord.Object(id=int(os.getenv('NSIG_SERVER'))))
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user, *, reason="No reason provided"):
        member = user
        if member[0] == '<' and member[-1] == '>':
            try:
                member = member[1:][:len(member) - 2].replace("@", "").replace("!", "")
            except (ValueError, TypeError):
                pass
        normal_ban = True
        user = None
        try:
            user = ctx.guild.get_member(int(member))
        except (ValueError, TypeError):
            pass
        if user is None:
            user = ctx.guild.get_member_named(member)
            if user is None:
                try:
                    user = await self.bot.fetch_user(member)
                    normal_ban = False
                except (discord.NotFound, discord.HTTPException):
                    embed = discord.Embed(description=f'**Member not found**', colour=error_colour)
                    await ctx.reply(embed=embed)
                    return
        try:
            await ctx.guild.fetch_ban(user)
            banned = True
        except (discord.NotFound, discord.HTTPException):
            banned = False
        if user.id == self.bot.user.id:
            embed = discord.Embed(description=f'**You cannot ban the bot**', colour=error_colour)
            await ctx.reply(embed=embed)
        elif user.id == ctx.author.id:
            embed = discord.Embed(description=f'**You cannot ban yourself**', colour=error_colour)
            await ctx.reply(embed=embed)
        elif user.id == ctx.guild.owner.id:
            embed = discord.Embed(description=f'**You cannot ban the owner of the server**', colour=error_colour)
            await ctx.reply(embed=embed)
        elif banned is True:
            embed = discord.Embed(description=f'**{user} is already banned**', colour=error_colour)
            await ctx.reply(embed=embed)
        elif ctx.author.id == ctx.guild.owner.id:
            await ban_func(ctx, user, reason, normal_ban)
        elif normal_ban is False:
            await ban_func(ctx, user, reason, normal_ban)
        elif user.top_role >= ctx.author.top_role:
            embed = discord.Embed(description=f'**You can only moderate members below your role**', colour=error_colour)
            await ctx.reply(embed=embed)
        else:
            await ban_func(ctx, user, reason, normal_ban)

    @commands.hybrid_command(name='unban', with_app_command=True, aliases=['ub'],
                             description=f'Unbans a user from the server', usage='[user]')
    @app_commands.describe(user='The user to unban')
    @app_commands.guilds(discord.Object(id=int(os.getenv('NSIG_SERVER'))))
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user):
        user_detail = user
        if user_detail[0] == '<' and user_detail[-1] == '>':
            try:
                user_detail = user_detail[1:][:len(user_detail) - 2].replace("@", "").replace("!", "")
            except (ValueError, TypeError):
                pass
        async for entry in ctx.guild.bans(limit=1000):
            if str(entry.user.id) == str(user_detail):
                member_id = entry.user.id
                break
            elif entry.user.name == user_detail:
                member_id = entry.user.id
                break
            elif f'{entry.user.name}#{entry.user.discriminator}' == user_detail:
                member_id = entry.user.id
                break
        else:
            embed = discord.Embed(description=f'**Member not banned**', colour=error_colour)
            await ctx.reply(embed=embed)
            return
        try:
            member = await self.bot.fetch_user(member_id)
        except (discord.NotFound, discord.HTTPException):
            embed = discord.Embed(description=f'**Member not found**', colour=error_colour)
            await ctx.reply(embed=embed)
            return
        await ctx.guild.unban(member)
        embed = discord.Embed(description=f'**{member} has been unbanned**',
                              colour=theme)
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name='unmute', with_app_command=True,
                             description=f'Unmutes a user in the server', usage='[user]')
    @app_commands.describe(user='The user to unmute')
    @app_commands.guilds(discord.Object(id=int(os.getenv('NSIG_SERVER'))))
    @commands.has_permissions(kick_members=True, ban_members=True)
    async def unmute(self, ctx, user: discord.Member):
        member = user
        muted_role = discord.utils.get(ctx.guild.roles, id=int(os.getenv('UNLUCKY_ROLE')))
        if muted_role not in member.roles:
            embed = discord.Embed(description=f'**User is not muted**', colour=error_colour)
            await ctx.reply(embed=embed)
        elif ctx.author.id == ctx.guild.owner.id:
            await member.remove_roles(muted_role)
            embed = discord.Embed(description=f'**{member} has been unmuted**',
                                  colour=theme)
            await ctx.reply(embed=embed)
            self.bot.dispatch('unmute', ctx, member, None)
        elif member.top_role >= ctx.author.top_role:
            embed = discord.Embed(description=f'**You can only moderate members below your role**',
                                  colour=error_colour)
            await ctx.reply(embed=embed)
        else:
            await member.remove_roles(muted_role)
            embed = discord.Embed(description=f'**{member} has been unmuted**',
                                  colour=theme)
            await ctx.reply(embed=embed)
            self.bot.dispatch('unmute', ctx, member, None)

    @commands.hybrid_command(name='mute', with_app_command=True,
                             description=f'Mutes a user in the server', usage='[member] (duration) (reason)')
    @app_commands.describe(user='The user to mute')
    @app_commands.describe(reason='The reason for muting the user')
    @app_commands.describe(time='The duration of the mute')
    @app_commands.guilds(discord.Object(id=int(os.getenv('NSIG_SERVER'))))
    @commands.has_permissions(kick_members=True)
    async def mute(self, ctx, user: discord.Member, time=None, *, reason=None):
        member = user
        role = discord.utils.get(ctx.guild.roles, id=int(os.getenv('UNLUCKY_ROLE')))
        if member.id == self.bot.user.id:
            embed = discord.Embed(description=f'**You cannot mute the bot**', colour=error_colour)
            await ctx.reply(embed=embed)
        elif member.id == ctx.author.id:
            embed = discord.Embed(description=f'**You cannot mute yourself**', colour=error_colour)
            await ctx.reply(embed=embed)
        elif member.id == ctx.guild.owner.id:
            embed = discord.Embed(description=f'**You cannot mute the owner of the server**', colour=error_colour)
            await ctx.reply(embed=embed)
        elif role in member.roles:
            embed = discord.Embed(description='**User is already muted**', colour=error_colour)
            await ctx.reply(embed=embed)
        elif ctx.author.id == ctx.guild.owner.id:
            await mute_func(self, ctx, member, time, reason)
        elif member.top_role >= ctx.author.top_role:  # checks if moderator is above target
            embed = discord.Embed(description=f'**You can only moderate members below your role**', colour=error_colour)
            await ctx.reply(embed=embed)
        else:
            await mute_func(self, ctx, member, time, reason)

    @commands.hybrid_command(name='purge', with_app_command=True, aliases=['clear', 'delete'],
                             description=f'Clears messages from a channel', usage='[amount] (user)')
    @app_commands.describe(user='The user whose messages will be purged')
    @app_commands.describe(amount='The number of messages to remove')
    @app_commands.guilds(discord.Object(id=int(os.getenv('NSIG_SERVER'))))
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount, user: discord.Member = None):
        member = user
        try:
            amount = int(amount)
        except (TypeError, ValueError):
            embed = discord.Embed(description=f'**Unable to convert amount to integer**', colour=error_colour)
            await ctx.reply(embed=embed)
            return
        i = 0
        if amount >= 101:
            embed = discord.Embed(description=f'**You can only purge up to 100 messages**', colour=error_colour)
            await ctx.reply(embed=embed)
            return
        else:
            if member is None:
                await ctx.channel.purge(limit=amount+1)
                embed = discord.Embed(description=f'**{amount} messages cleared**', colour=theme)
                await ctx.send(embed=embed, delete_after=5.0)
                self.bot.dispatch('clear', ctx, amount, None, None)
                return
            elif member is not None:
                if ctx.author.id == member.id:
                    amount = amount + 1
                elif member.id == self.bot.user.id:
                    pass
                elif member.top_role >= ctx.author.top_role:
                    embed = discord.Embed(description=f'**You can only moderate members below your role**',
                                          colour=error_colour)
                    await ctx.reply(embed=embed)
                    return
                grab = []
                if i <= amount:
                    async for one_message in ctx.channel.history(limit=500):
                        if i < amount:
                            if one_message.author.id == member.id:
                                grab.append(one_message)
                                i += 1
                        elif i >= amount:
                            break
                    try:
                        await ctx.channel.delete_messages(grab)
                    except (discord.HTTPException, discord.ClientException):
                        embed = discord.Embed(description=f'**Messages older than 14 days**', colour=error_colour)
                        await ctx.send(embed=embed)
                        return
        if i == 0:
            embed = discord.Embed(description=f'**No messages cleared**', colour=error_colour)
            await ctx.send(embed=embed, delete_after=5.0)
        elif i != 0:
            embed = discord.Embed(description=f'**{i} messages cleared**', colour=theme)
            await ctx.send(embed=embed, delete_after=5.0)
            self.bot.dispatch('clear', ctx, amount, i, member)
        try:
            await asyncio.sleep(5)
            await ctx.message.delete()
        except (discord.Forbidden, discord.NotFound, discord.HTTPException):
            pass


async def setup(bot) -> None:
    await bot.add_cog(Moderation(bot))
