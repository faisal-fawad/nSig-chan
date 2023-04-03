# Common imports in all python files
from discord.ext import commands
import discord
from discord import app_commands
from datetime import datetime
from pytz import timezone


# Used in all python files
tz = timezone('US/Eastern')
theme = discord.Colour.green()
error_colour = discord.Colour.red()
argument_colour = discord.Colour.orange()
