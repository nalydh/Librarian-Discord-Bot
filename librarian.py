import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv("token.env")

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')


bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

bot.run(DISCORD_TOKEN)