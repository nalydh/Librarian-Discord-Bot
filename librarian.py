import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import time

load_dotenv("token.env")

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.command()
async def template(message):
    channel = message.channel
    summary_template = "Reading **(Book Title)** (chapter (**Chapter Number**)):\n# Chapter Title \n## ⭐️ Lessons Learnt\n- Paragraph 1\n- Paragraph 2\n- Paragraph ..."
    await channel.send(summary_template)
    await message.message.delete(delay=2)


bot.run(DISCORD_TOKEN)