import os
import re
import json
from universal import *


class General(commands.Cog, name="General"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.filtered_words = json.loads(os.getenv('FILTERED_WORDS'))
        self.very_bad_filtered_words = json.loads(os.getenv('VERY_BAD_FILTERED_WORDS'))

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user: discord.Member):
        entry = await guild.fetch_ban(user)
        reason = entry.reason
        ban_log = discord.Embed(colour=theme, timestamp=datetime.now(tz))
        ban_log.set_author(name=f'{user} has been banned', icon_url=user.display_avatar)
        ban_log.add_field(name='Reason:', value=reason)
        ban_log.set_footer(text=f'ID: {user.id}')
        channel = self.bot.get_channel(int(os.getenv('GENERAL_LOGS')))
        await channel.send(embed=ban_log)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user: discord.Member):
        unban_log = discord.Embed(colour=error_colour, timestamp=datetime.now(tz))
        unban_log.set_author(name=f'{user} has been unbanned', icon_url=user.display_avatar)
        unban_log.set_footer(text=f'ID: {user.id}')
        channel = self.bot.get_channel(int(os.getenv('GENERAL_LOGS')))
        await channel.send(embed=unban_log)

    @commands.Cog.listener()
    async def on_unmute(self, ctx, member, moderator):
        if moderator is None:
            moderator = ctx.author.mention
        unmute_log = discord.Embed(colour=error_colour, timestamp=datetime.now(tz))
        unmute_log.set_author(name=f'{member} has been unmuted', icon_url=member.display_avatar)
        unmute_log.add_field(name='Moderator:', value=moderator)
        unmute_log.set_footer(text=f'ID: {member.id}')
        channel = self.bot.get_channel(int(os.getenv('GENERAL_LOGS')))
        await channel.send(embed=unmute_log)

    @commands.Cog.listener()
    async def on_mute(self, ctx, member, time, reason):
        mute_log = discord.Embed(colour=theme, timestamp=datetime.now(tz))
        mute_log.set_author(name=f'{member} has been muted', icon_url=member.display_avatar)
        mute_log.add_field(name='Moderator:', value=ctx.author.mention)
        mute_log.add_field(name='Length:', value=time)
        mute_log.add_field(name='Reason:', value=reason)
        mute_log.set_footer(text=f'ID: {member.id}')
        channel = self.bot.get_channel(int(os.getenv('GENERAL_LOGS')))
        await channel.send(embed=mute_log)

    @commands.Cog.listener()
    async def on_message_filter(self, message):
        message_content = message.content.lower()
        highlighted_message = message.content
        remove_links = re.compile('https://', re.IGNORECASE)
        highlighted_message = remove_links.sub('', highlighted_message)
        if any(word in message_content for word in self.very_bad_filtered_words):
            for one in self.very_bad_filtered_words:
                replacement = re.compile(one, re.IGNORECASE)
                highlighted_message = replacement.sub(f'__{one}__', highlighted_message)
            await message.delete()
            self.bot.dispatch('filtered', message, highlighted_message, 'High')
        elif any(word in message_content for word in self.filtered_words):
            if message.channel.id == int(os.getenv('BOOFTOP_CHANNEL')):
                pass
            else:
                for one in self.filtered_words:
                    replacement = re.compile(one, re.IGNORECASE)
                    highlighted_message = replacement.sub(f'__{one}__', highlighted_message)
                await message.delete()
                self.bot.dispatch('filtered', message, highlighted_message, 'Medium')

    @commands.Cog.listener()
    async def on_filtered(self, message, new_message, strength):
        censor_log = discord.Embed(description=new_message, colour=theme,
                                   timestamp=datetime.now(tz))
        censor_log.set_author(name=f'Deleted Message', icon_url=message.author.display_avatar)
        censor_log.add_field(name='User:',
                             value=f'{message.author}')
        censor_log.add_field(name='Channel:', value=message.channel.mention, inline=False)
        censor_log.add_field(name='Filter:', value=f'{strength}')
        censor_log.set_footer(text=f'ID: {message.author.id}')
        channel = self.bot.get_channel(int(os.getenv('GENERAL_LOGS')))
        await channel.send(embed=censor_log)
        if strength == "High":
            await channel.send(f'<@&{os.getenv("MOD_ROLE")}> High filter triggered above by ID: `{message.author.id}`')

    @commands.Cog.listener()
    async def on_kick(self, ctx, user, reason):
        kick_log = discord.Embed(colour=theme, timestamp=datetime.now(tz))
        kick_log.set_author(name=f'{user} has been kicked',
                            icon_url=user.display_avatar)
        kick_log.add_field(name='Moderator:', value=f'{ctx.author.mention}')
        kick_log.add_field(name='Reason:', value=reason)
        kick_log.set_footer(text=f'ID: {user.id}')
        channel = self.bot.get_channel(int(os.getenv('GENERAL_LOGS')))
        await channel.send(embed=kick_log)

    @commands.Cog.listener()
    async def on_clear(self, ctx, amount, cleared, member):
        if member is None:
            clear_log = discord.Embed(colour=theme, timestamp=datetime.now(tz))
            clear_log.set_author(name=f'{ctx.author} cleared messages',
                                 icon_url=ctx.author.display_avatar)
            clear_log.add_field(name=f'Amount:', value=amount)
            clear_log.add_field(name=f'Moderator:', value=ctx.author.mention)
            clear_log.add_field(name=f'Channel:', value=ctx.channel.mention)
            channel = self.bot.get_channel(int(os.getenv('GENERAL_LOGS')))
            await channel.send(embed=clear_log)
        else:
            clear_log = discord.Embed(colour=theme, timestamp=datetime.now(tz))
            clear_log.set_author(name=f'{ctx.author} cleared messages',
                                 icon_url=ctx.author.display_avatar)
            clear_log.add_field(name=f'Attempted Amount:', value=f'{amount}')
            clear_log.add_field(name=f'Deleted Amount:', value=f'{cleared}')
            clear_log.add_field(name=f'Moderator:', value=ctx.author.mention)
            clear_log.add_field(name=f'User Deleted:', value=f'{member}')
            clear_log.add_field(name=f'Channel:', value=ctx.channel.mention)
            clear_log.set_footer(text=f'ID: {member.id}')
            channel = self.bot.get_channel(int(os.getenv('GENERAL_LOGS')))
            await channel.send(embed=clear_log)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return
        if message.author.bot:
            return
        if message.channel.type == discord.ChannelType.private:
            return
        self.bot.dispatch('message_filter', message)


async def setup(bot):
    await bot.add_cog(General(bot))
