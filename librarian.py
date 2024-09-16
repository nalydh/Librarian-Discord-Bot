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
    '''
    This command method is called by !template
    Sends a warning message about the deletion of the template and then waits for users to read this warning, after 3 seconds, the template is sent. After 10 seconds, the warning and template messages are deleted for cleanliness.    
    '''
    # Gets the context's channel 
    channel = message.channel
    # Summary template string
    summary_template = "\nReading **(Book Title)** (chapter (**Chapter Number**)):\n# Chapter Title \n## ⭐️ Lessons Learnt\n- Paragraph 1\n- Paragraph 2\n- Paragraph ..."
    # Warning of deletion message string
    warning_message = "**WARNING:** This template will be deleted after __10 seconds__. Copy the text quickly!\n"
    # Deletes the !template message straight away
    await message.message.delete()
    # Let's the users know that the template will be deleted after 10 seconds
    bot_output_warning = await channel.send(warning_message)
    # Wait 3 seconds
    time.sleep(3)
    # Sends the template to the channel the command was executed in
    bot_output_template = await channel.send(summary_template)
    # Deletes both the warning and template messages after 10 seconds of being sent.
    await bot_output_warning.delete(delay=10)
    await bot_output_template.delete(delay=10)


bot.run(DISCORD_TOKEN)