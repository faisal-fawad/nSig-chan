import os
from universal import *


class Message(commands.Cog, name="Message"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        cleaned_message_before = before.clean_content
        cleaned_message_after = after.clean_content
        if before.channel.type == discord.ChannelType.private:
            return
        if before is None:
            return
        if after is None:
            return
        if before.author.bot is True:
            return
        if before.author.id == self.bot.user.id:
            return
        elif before.content != after.content:
            channel = self.bot.get_channel(int(os.getenv('MESSAGE_LOGS')))
            time = str(datetime.now(tz)).split(" ")[1]
            await channel.send(f'[`{str(time).split(".")[0]}`] **{before.author.name}#{before.author.discriminator}** '
                               f'(`{before.author.id}`) **edited** a message in {before.channel.mention}:'
                               f'\n**Before:** {cleaned_message_before} \n**After:** {cleaned_message_after}')
            self.bot.dispatch('message_filter', after)

    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, payload):
        channel = self.bot.get_channel(int(os.getenv('MESSAGE_LOGS')))
        messages = payload.cached_messages
        if messages is None:
            return
        time = str(datetime.now(tz)).split(" ")[1]
        grab = []
        message_channel = ""
        for one_message in messages:
            message = one_message.clean_content
            if message is None:
                pass
            else:
                message_channel = one_message.channel.mention
                formatted_message = f'{one_message.author} ({one_message.author.id}): {message} \n'
                grab.append(formatted_message)
        split_grab = [grab[x:x + 50] for x in range(0, len(grab), 50)]
        for element in split_grab:
            text = ''
            for one in element:
                text = text + one
            with open("result.txt", "w") as f:
                f.write(text)
            with open("result.txt", "rb") as f:
                if message_channel is None:
                    content = ""
                else:
                    content = f"in {message_channel}"
                await channel.send(f'[`{str(time).split(".")[0]}`] Multiple messages **deleted** {content}: \n',
                                   file=discord.File("result.txt", "result.txt"))
                f.close()

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        message = payload.cached_message
        if message is None:
            return
        if message.channel.type == discord.ChannelType.private:
            return
        if message.author.bot is True:
            return
        if message.author.id == self.bot.user.id:
            return
        cleaned_message = message.clean_content
        channel = self.bot.get_channel(int(os.getenv('MESSAGE_LOGS')))

        now = datetime.utcnow()
        get_difference = message.created_at.strftime("%H:%M:%S")
        then = datetime.strptime(f'{get_difference}', '%H:%M:%S')
        then = datetime.combine(now.date(), then.time())

        real_time = str(datetime.now(tz)).split(" ")[1]
        real_time = str(real_time).split(".")[0]

        delta = now - then
        sent = message.created_at.strftime("%D")
        deleted = now.strftime("%D")

        if sent == deleted:
            delta = f'{delta}'
            delta = delta.split(".")[0]
        elif sent != deleted:
            delta = f'Over 1 day'

        if len(message.attachments) > 0:
            attachment_list = ''
            for one in message.attachments:
                attachment_list = f'{attachment_list + one.proxy_url} \n'
            try:
                await channel.send(
                    f'[`{real_time}`] **{message.author}**'
                    f' (`{message.author.id}`) **deleted** a message in {message.channel.mention} ({delta})'
                    f'\n**Content:** {cleaned_message}'
                    f'\n**Attachment(s):** {attachment_list}')
            except discord.HTTPException:
                with open("result.txt", "w") as f:
                    f.write(f'**Content:**\n {cleaned_message}'
                            f'\n**Attachment(s):**\n {attachment_list}')
                with open("result.txt", "rb") as f:
                    await channel.send(
                        f'[`{real_time}`] **{message.author}**'
                        f' (`{message.author.id}`) **deleted** a message in {message.channel.mention} ({delta})',
                        file=discord.File("result.txt", "result.txt"))
                    f.close()
        elif len(message.attachments) == 0:
            try:
                await channel.send(
                    f'[`{real_time}`] **{message.author}**'
                    f' (`{message.author.id}`) **deleted** a message in {message.channel.mention} ({delta})'
                    f'\n**Content:** {cleaned_message}')
            except discord.HTTPException:
                with open("result.txt", "w") as f:
                    f.write(f'{cleaned_message}')
                with open("result.txt", "rb") as f:
                    await channel.send(
                        f'[`{real_time}`] **{message.author}**'
                        f' (`{message.author.id}`) **deleted** a message in {message.channel.mention} ({delta})',
                        file=discord.File("result.txt", "result.txt"))
                    f.close()


async def setup(bot) -> None:
    await bot.add_cog(Message(bot))
