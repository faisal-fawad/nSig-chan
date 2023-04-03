import os
from pymongo import MongoClient
from universal import *


# MongoDB information
cluster = MongoClient(os.getenv("MONGO_TOKEN"))
db = cluster["discord"]
collection = db["bracket"]


class SendButtons(discord.ui.View):
    def __init__(self, ctx, channel, response, message):
        super().__init__(timeout=120)
        self.response = response
        self.ctx = ctx
        self.msg = message
        self.channel = channel

    async def on_timeout(self):
        self.clear_items()
        await self.response.edit(view=self)

    async def interaction_check(self, interaction) -> bool:
        if interaction.user != self.ctx.author:
            return False
        else:
            return True

    @discord.ui.button(label='Send anyway', style=discord.ButtonStyle.green, custom_id='1')
    async def sent(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.disabled = True
        jump = await self.channel.send(self.msg)
        embed = discord.Embed(description=f"**Message [sent]({jump.jump_url})**",
                              colour=theme)
        await interaction.response.edit_message(embed=embed, view=self)
        self.clear_items()
        await self.response.edit(view=self)


class MemberButtons(discord.ui.View):
    def __init__(self, ctx, embeds, last_page, response):
        super().__init__(timeout=300)
        self.response = response
        self.ctx = ctx
        self.embeds = embeds
        self.page_number = 0
        self.max_page = last_page

    async def on_timeout(self):
        self.clear_items()
        await self.response.edit(view=self)

    async def interaction_check(self, interaction) -> bool:
        if interaction.user != self.ctx.author:
            return False
        else:
            return True

    @discord.ui.button(label='<<', style=discord.ButtonStyle.green, custom_id='l', disabled=True)
    async def left(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page_number = self.page_number - 1
        if self.page_number < 0:
            self.page_number = 0
        if self.page_number == 0:
            button.disabled = True
        else:
            button.disabled = False
        for one in self.children:
            if one.custom_id == 'r':
                one.disabled = False
        await interaction.response.edit_message(embed=self.embeds[self.page_number], view=self)

    @discord.ui.button(label='>>', style=discord.ButtonStyle.green, custom_id='r')
    async def right(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page_number = self.page_number + 1
        if self.page_number > self.max_page:
            self.page_number = self.max_page
        if self.page_number == self.max_page:
            button.disabled = True
        else:
            button.disabled = False
        for one in self.children:
            if one.custom_id == 'l':
                one.disabled = False
        await interaction.response.edit_message(embed=self.embeds[self.page_number], view=self)


class Private(commands.Cog, name="Private"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name='updatebracket', with_app_command=True,
                             description=f'Updates the bracket link', usage='[url]')
    @app_commands.describe(link='The link to the bracket')
    @app_commands.guilds(discord.Object(id=int(os.getenv('NSIG_SERVER'))))
    @commands.has_any_role(793387151148318720, 503631961185845269, 735685683716423691)
    async def updatebracket(self, ctx, *, link):
        collection.delete_one({"_id": "bracket"})
        post = {"_id": "bracket", "bracket": f'{link}'}
        collection.insert_one(post)
        embed = discord.Embed(description=f'**Link updated**', colour=theme)
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name='members', with_app_command=True,
                             description=f'Shows the members of a role', usage='[role]')
    @app_commands.describe(role='The role to check which members have')
    @app_commands.guilds(discord.Object(id=int(os.getenv('NSIG_SERVER'))))
    @commands.has_permissions(manage_roles=True)
    async def members(self, ctx, *, role: discord.Role):
        server = self.bot.get_guild(int(os.getenv('NSIG_SERVER')))
        i = 0
        members = []
        if role.id == int(os.getenv('UNLUCKY_ROLE')):
            for member in server.members:
                if role in member.roles:
                    i += 1
                    name = f'**{str(i)}:** {member} - `{member.id}` \n'
                    members.append(name)
        else:
            for member in server.members:
                if role in member.roles:
                    i += 1
                    name = f'**{str(i)}:** {member} \n'
                    members.append(name)
        separate_members = [members[x:x + 20] for x in range(0, len(members), 20)]
        pages = []
        if i == 0:
            embed = discord.Embed(title=f"Members with role - {role}", colour=theme)
            embed.set_footer(text=f'0 members have this role')
            pages.append(embed)
        else:
            for elements in separate_members:
                string = ""
                for one in elements:
                    string = string + one
                embed = discord.Embed(title=f"Members with role - {role}", colour=theme)
                embed.add_field(name="Members:", value=string)
                if i == 1:
                    embed.set_footer(text=f'{i} member has this role')
                else:
                    embed.set_footer(text=f'{i} members have this role')
                pages.append(embed)
        last = len(pages) - 1
        embed = discord.Embed(timestamp=datetime.now(tz), description=f'**Loading...**',
                              colour=theme)
        msg = await ctx.reply(embed=embed)
        await msg.edit(embed=pages[0], view=MemberButtons(embeds=pages, last_page=last, ctx=ctx, response=msg))

    @commands.hybrid_command(name='serverinfo', with_app_command=True,
                             description=f'Shows info on the server', usage='')
    @app_commands.guilds(discord.Object(id=int(os.getenv('NSIG_SERVER'))))
    async def serverinfo(self, ctx):
        guild_created = str(ctx.guild.created_at)
        embed = discord.Embed(
            description=f'**Description:** {ctx.guild.description}',
            color=theme,
            timestamp=datetime.now(tz)
        )
        embed.set_thumbnail(url=ctx.guild.icon)
        embed.set_author(name=f'{ctx.guild.name} - Server Information',
                         icon_url=ctx.guild.icon)
        embed.add_field(name="Owner:", value=ctx.guild.owner)
        embed.add_field(name="Server ID:", value=f'`{ctx.guild.id}`')
        embed.add_field(name="Member Count:", value=ctx.guild.member_count)
        embed.add_field(name="Role Count:", value=len(ctx.guild.roles))
        embed.add_field(name="Server Creation:", value=guild_created.split(" ")[0])
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name='poll', with_app_command=True,
                             description=f'Creates a poll', usage='[question] [options]')
    @app_commands.describe(question='The question to ask')
    @app_commands.describe(options='Answers to the question being asked; Separate answers with a comma')
    @app_commands.guilds(discord.Object(id=int(os.getenv('NSIG_SERVER'))))
    @commands.has_permissions(kick_members=True)
    async def poll(self, ctx, question, *, options):
        commas = options.count(",")
        spaces = options.count(" ")
        if commas >= 1:
            split_options = str(options).split(",")
            if commas > 8:
                embed = discord.Embed(description=f'**Max number of options is 8**', colour=error_colour)
                await ctx.reply(embed=embed)
                return
        elif spaces >= 1:
            split_options = str(options).split(" ")
            if spaces > 7:
                embed = discord.Embed(description=f'**Max number of options is 8**', colour=error_colour)
                await ctx.reply(embed=embed)
                return
        else:
            embed = discord.Embed(description=f'**Options entered incorrectly**', colour=error_colour)
            await ctx.reply(embed=embed)
            return
        poll_embed = discord.Embed(title=f'Poll', colour=theme, timestamp=datetime.now(tz),
                                   description=f'**Question:** {question}')
        i = 0
        numbers = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣']
        for option in split_options:
            number = numbers[i]
            poll_embed.add_field(name=f'Option {number}:', value=f'{option}', inline=False)
            i += 1

        message = await ctx.reply(embed=poll_embed)
        total = numbers[0:i]
        for one in total:
            await message.add_reaction(one)

    @commands.hybrid_command(name='send', with_app_command=True,
                             description=f'Sends a message through nSig-chan', usage='[channel] [message]')
    @app_commands.describe(channel='The channel to send the message')
    @app_commands.describe(channel='The message to send')
    @app_commands.guilds(discord.Object(id=int(os.getenv('NSIG_SERVER'))))
    @commands.has_any_role(503631961185845269, 735685683716423691, 793387151148318720, 906540401517805588)
    async def send(self, ctx, channel: discord.TextChannel, *, message):
        if "@everyone" in message or "@here" in message:
            loading = discord.Embed(timestamp=datetime.now(tz), description=f'**Loading...**',
                                    colour=theme)
            msg = await ctx.reply(embed=loading)
            embed = discord.Embed(description=f'**This message contains @everyone or @here and '
                                              f'is being sent to {channel.mention}**',
                                  colour=error_colour)
            await msg.edit(embed=embed, view=SendButtons(ctx=ctx, response=msg, message=message, channel=channel))
        else:
            msg = await channel.send(message)
            embed = discord.Embed(description=f"**Message [sent]({msg.jump_url})**",
                                  colour=theme)
            await ctx.reply(embed=embed)


async def setup(bot) -> None:
    await bot.add_cog(Private(bot))
