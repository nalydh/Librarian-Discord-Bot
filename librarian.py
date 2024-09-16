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
    summary_template = "\nReading **(Book Title)** (chapter (**Chapter Number**)):\n# Chapter Title \n## ⭐️ Lessons Learnt\n- Paragraph 1\n- Paragraph 2\n- Paragraph ..."
    warning_message = "**WARNING:** This template will be deleted after __10 seconds__. Copy the text quickly!\n"
    bot_output_warning = await channel.send(warning_message)
    bot_output_template = await channel.send(summary_template)
    await message.message.delete(delay=0.1)
    await bot_output_warning.delete(delay=10)
    await bot_output_template.delete(delay=10)


bot.run(DISCORD_TOKEN)