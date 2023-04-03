import os
from dotenv import load_dotenv
from universal import *


# Loading .env file
load_dotenv()


# A custom help command for individual discord commands
class CustomHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title=f'Help Command', timestamp=datetime.now(tz), colour=theme,
                              description=f'`{os.getenv("BOT_PREFIX")}help (class/command)`')
        for cog in mapping:
            if cog is None:
                pass
            elif len(mapping[cog]) == 0:
                pass
            else:
                title = cog.qualified_name
                cog_commands = f''
                for command in mapping[cog]:
                    cog_commands = cog_commands + f'`{os.getenv("BOT_PREFIX")}{command.name}` \n'
                embed.add_field(name=f'{title}:', value=cog_commands, inline=False)
        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog):
        cog_commands = f''
        for command in cog.get_commands():
            cog_commands = cog_commands + f'`{os.getenv("BOT_PREFIX")}{command.name}` : ' \
                                          f'{command.description} \n'
        embed = discord.Embed(title=f'{cog.qualified_name} Commands:', timestamp=datetime.now(tz), colour=theme,
                              description=cog_commands)
        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
        e = discord.Embed(timestamp=datetime.now(tz),
                          colour=argument_colour,
                          description=f'`{os.getenv("BOT_PREFIX")}{command.name} {command.usage}`')
        await self.get_destination().send(embed=e)

    async def send_error_message(self, error):
        embed = discord.Embed(description=f'**Class/command not found**', colour=error_colour)
        await self.get_destination().send(embed=embed)


# Settings for the discord bot
intents = discord.Intents.all()
activity = discord.Activity(name="Brawlhalla", type=discord.ActivityType.competing)
helper = CustomHelpCommand()
owner = 437274901435514891


# Bot class
class Bot(commands.Bot):
    def __init__(self, command_prefix):
        super().__init__(command_prefix=command_prefix, intents=intents, help_command=helper,
                         activity=activity, owner_id=owner, case_insensitive=True)

    async def setup_hook(self):
        for folder in os.listdir(f'./cogs'):
            for file in os.listdir(f'./cogs/{folder}'):
                if file.endswith('.py'):
                    await self.load_extension(f'cogs.{folder}.{file[:-3]}')
        await self.tree.sync(guild=discord.Object(id=int(os.getenv('NSIG_SERVER'))))
        print('Tree synced!')

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')


# Running bot
bot = Bot(command_prefix=str(os.getenv('BOT_PREFIX')))
bot.run(str(os.getenv('BOT_TOKEN')))
