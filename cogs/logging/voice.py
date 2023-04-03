import os
from universal import *


class Voice(commands.Cog, name="Voice"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before, after):
        channel = self.bot.get_channel(int(os.getenv('VOICE_LOGS')))
        if before.channel is not None and after.channel is None:
            embed = discord.Embed(colour=discord.Colour.red(), timestamp=datetime.now(tz),
                                  description=f'has left {before.channel.mention}')
            embed.set_author(name=f'{member}', icon_url=member.display_avatar)
            embed.set_footer(text=f'ID: {member.id}')
            await channel.send(embed=embed)
        elif before.channel is not None and after.channel is not None:
            if after.deaf or after.mute or after.requested_to_speak_at or after.self_deaf or after.self_mute or \
                    after.self_stream or after.self_video or after.suppress:
                return
            elif before.deaf or before.mute or before.requested_to_speak_at or before.self_deaf or before.self_mute or \
                    before.self_stream or before.self_video or before.suppress:
                return
            embed = discord.Embed(colour=discord.Colour.gold(), timestamp=datetime.now(tz),
                                  description=f'has moved from {before.channel.mention} to {after.channel.mention}')
            embed.set_author(name=f'{member}', icon_url=member.display_avatar)
            embed.set_footer(text=f'ID: {member.id}')
            await channel.send(embed=embed)
        elif before.channel is None and after.channel is not None:
            embed = discord.Embed(colour=discord.Colour.green(), timestamp=datetime.now(tz),
                                  description=f'has joined {after.channel.mention}')
            embed.set_author(name=f'{member}', icon_url=member.display_avatar)
            embed.set_footer(text=f'ID: {member.id}')
            await channel.send(embed=embed)
        else:
            return


async def setup(bot) -> None:
    await bot.add_cog(Voice(bot))
