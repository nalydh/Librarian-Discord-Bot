import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import time
import datetime

load_dotenv("token.env")

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

streaks = {}

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

    send_leaderboard.start()
    
@bot.command()
async def template(message):
    '''
    This command method is called by !template
    Sends a warning message about the deletion of the template and then waits for users to read this warning, after 3 seconds, the template is sent. After 10 seconds, the warning and template messages are deleted for cleanliness.    
    '''
    # Gets the context's channel 
    channel = message.channel
    # Summary template string
    summary_template = (
        "# Chapter Summary:\n"
        "`chapter number/title` \n"
        "## ⭐️ Lessons Learnt\n"
        "- Paragraph 1\n"
        "- Paragraph 2\n"
        "- Paragraph ..."
        )
    # Warning of deletion message string
    warning_message = "**WARNING:** This template will be deleted after __10 seconds__. Copy the text quickly!"
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

@bot.event
async def on_message(message):
    user_id = message.author.id
    channel = message.channel
    current_date = datetime.datetime.now().date()
    if message.content.startswith("# Chapter Summary:"):
        if user_id in streaks: 
            streak_count, last_entry_date = streaks[user_id] 

            if last_entry_date == current_date:
                await channel.send(f"{message.author.mention}, you have already entered your chapter entry for today! :low_battery:")
            elif last_entry_date < current_date:
                streaks[user_id] = (streak_count + 1, current_date)
                await channel.send(f"{message.author.mention}, you have logged your chapter entry for today! Keep it up!")


        else:
            streaks[user_id] = (1, current_date)

    await bot.process_commands(message)


        

# User ID: streak_counter
start_time = datetime.datetime(year=2024, month=9, day=18, hour=0, minute=0, second=0)
target_time = datetime.datetime(year=2024, month=9, day=19, hour=0, minute=0, second=0)

@bot.command()
async def streak(message):
    user_id = message.author.id
    channel = message.channel

    if user_id in streaks:
        streak_count, _ = streaks[user_id]
        if streak_count == 1:
            await channel.send(f"{message.author.mention}, you've started a streak 🔥! **{streaks[user_id]} day** logged.")
        else: 
            await channel.send(f"{message.author.mention}, your current streak 🔥 is **{streaks[user_id]} days!**")
    else:
        await channel.send(f"{message.author.mention}, you haven't started a streak yet. 😢")

@tasks.loop(hours=24)
async def send_leaderboard():
    current_time = datetime.now()
    if current_time.hour == 8:
        # leaderboard text channel
        channel = bot.get_channel(1286228895858819134)
        current_date = datetime.datetime.now().strftime("%d-%m-%Y")
        
        # Initial leaderboard message
        leaderboard_message = f"`{current_date}`\nCurrent leaders of the 4D Book Club 📖\n\n**Name:**ᅠᅠᅠᅠᅠᅠᅠᅠᅠ**Streak:**\n"
        
        # Sort streaks and add entries to the leaderboard
        sorted_streaks = sorted(streaks.items(), key = lambda x: x[1][0], reverse=True)
        for user_id, streak_count in sorted_streaks:
            username = bot.get_user(user_id)
            leaderboard_message += f"{username.mention}ᅠᅠᅠᅠᅠᅠᅠᅠᅠ{streak_count} days\n"
        
        # Create the embedded message
        embedded_msg = discord.Embed(title="**⭐ 2024 Leaderboard ⭐**", description=leaderboard_message, color=discord.Color.green())

        # Send the message to the channel
        await channel.send(embed=embedded_msg)




bot.run(DISCORD_TOKEN)