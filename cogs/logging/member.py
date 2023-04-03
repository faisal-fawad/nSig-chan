import os
from universal import *


class Member(commands.Cog, name="Member"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.reactions = {'🇦': 902263088546455562, '🇧': 902263161200189480, '🇨': 902263203411660860,
                          '🇩': 902263403496759296,
                          '🇪': 902263644237209630, '🇫': 902263764747964446, '🇬': 902263828119715851,
                          '🇭': 902263910319677480,
                          '🇮': 902264147109101568, '🇯': 902264183352074312, '🇰': 902282513978916865,
                          '🇱': 902264345847824394,
                          '🇲': 902264400579268659, '🇳': 902264461178585169, '🇴': 902264524256735283,
                          '🇵': 902264625163280404,
                          '🇶': 902264691055820800, '🇷': 902263968909901866}
        '🇦  🇧  🇨  🇩  🇪  🇫  🇬  🇭  🇮  🇯  🇰  🇱  🇲  🇳  🇴  🇵  🇶  🇷  🇸  🇹  🇺  🇻  🇼  🇽  🇾  🇿 '

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id == 902285183888281670:
            channel = await self.bot.fetch_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            for emoji in self.reactions:
                if str(emoji) == str(payload.emoji):
                    role_id = self.reactions.get(emoji)
                    role = discord.utils.get(message.guild.roles, id=role_id)
                    await payload.member.add_roles(role)
            for r in message.reactions:
                users = [user async for user in r.users()]
                if payload.member in users and not payload.member.bot and str(r) != str(
                        payload.emoji):
                    await message.remove_reaction(r.emoji, payload.member)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.message_id == 902285183888281670:
            channel = await self.bot.fetch_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            for emoji in self.reactions:
                if str(emoji) == str(payload.emoji):
                    role_id = self.reactions.get(emoji)
                    role = discord.utils.get(message.guild.roles, id=role_id)
                    member = await message.guild.fetch_member(payload.user_id)
                    await member.remove_roles(role)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        channel = self.bot.get_channel(int(os.getenv('MEMBER_LOGS')))
        if before.roles != after.roles:
            b = set(before.roles)
            a = set(after.roles)
            if len(before.roles) < len(after.roles):
                new_roles = [x for x in after.roles if x not in b]
                content = "given"
                border_color = theme
            elif len(before.roles) > len(after.roles):
                new_roles = [x for x in before.roles if x not in a]
                content = "removed from"
                border_color = error_colour
            else:
                return
            if len(new_roles) >= 1:
                nsig_booster = int(os.getenv('NSIG_BOOSTER'))
                nsig_subscriber = int(os.getenv('NSIG_SUBSCRIBER'))
                if content == "removed from":
                    if any((int(nr.id) == nsig_booster or int(nr.id) == nsig_subscriber) for nr in new_roles):
                        role_ids = []
                        for role in before.roles:
                            role_ids.append(role.id)
                        for one_reaction in self.reactions:
                            color_role = self.reactions.get(one_reaction)
                            if color_role in role_ids:
                                final_role = discord.utils.get(before.guild.roles, id=color_role)
                                await before.remove_roles(final_role)
                new_role_mention = []
                for one in new_roles:
                    new_role_mention.append(one.mention)
                role_str = ", ".join(new_role_mention)
                embed = discord.Embed(colour=border_color, timestamp=datetime.now(tz),
                                      description=f'was {content} the **{role_str}** role(s)')
                embed.set_author(name=f'{before}', icon_url=before.display_avatar)
                embed.set_footer(text=f'ID: {before.id}')
                await channel.send(embed=embed)
        elif before.nick != after.nick:
            old_nick = before.nick
            new_nick = after.nick
            if before.nick == before.name:
                old_nick = None
            elif after.nick == after.name:
                new_nick = None
            embed = discord.Embed(colour=theme, timestamp=datetime.now(tz),
                                  description=f'**Before:** {old_nick} \n'
                                              f'**After:** {new_nick}')
            embed.set_author(name=f'{before} nickname changed',
                             icon_url=before.display_avatar)
            embed.set_footer(text=f'ID: {before.id}')
            await channel.send(embed=embed)


async def setup(bot) -> None:
    await bot.add_cog(Member(bot))
