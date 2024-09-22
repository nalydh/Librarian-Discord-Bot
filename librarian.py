import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import asyncio
from datetime import datetime, timedelta
import pytz

load_dotenv("token.env")

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Set timezone to AEST
AEST = pytz.timezone('Australia/Sydney')

# Initialise Bot Class
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# Streaks dictionary that stores a tuple {user_id: (streak_count, last_entry_date}
streaks = {}

@bot.event
async def on_ready():
    '''
    This command method is called when the bot goes online.
    Prints a simple message to notify that the bot is running and starts regular tasks methods   
    '''

    print(f'{bot.user.name} has connected to Discord!')

    send_leaderboard.start()
    check_deadline.start()
    
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
    await asyncio.sleep(2)
    
    # Sends the template to the channel the command was executed in
    bot_output_template = await channel.send(summary_template)
    
    # Deletes both the warning and template messages after 10 seconds of being sent.
    await bot_output_warning.delete(delay=10)
    await bot_output_template.delete(delay=10)

@bot.event
async def on_message(message):
    '''
    Command that triggers everytime a message is sent on the server.
    Will do a check to do log_chapter after every message (may seem wasteful but rather than then by logging using commands)
    '''

    if message.author.bot:
        return
    
    if message.content.startswith("# Chapter Summary:"):
        await log_chapter(message)

    # Since this method overwrites on_message, we still need to allow bots to process commands.
    await bot.process_commands(message)

async def log_chapter(message):
    '''
    Checks to see if the message starts with # Chapter Summary: to log chapter and increment streak.
    It also starts a new streak if they are not in streaks dictionary already.
    '''
    
    user_id = message.author.id
    channel = message.channel

    # Create datetime object 
    current_date = datetime.now()

    # Store values from streaks dictionary
    if user_id in streaks: 
        streak_count, last_entry_date = streaks[user_id] 

        # If the date (YYYY-MM-DD) of last entry is same as today then you cannot log another chapter
        if last_entry_date == current_date:
            await channel.send(f"{message.author.mention}, you have already entered your chapter entry for today! 👍")
        
        # If the date of last entry is less than current date, then you can log a chapter.
        elif last_entry_date < current_date:
            streaks[user_id] = (streak_count + 1, current_date)
            await channel.send(f"{message.author.mention}, you have logged your chapter entry for today! Keep it up!")

    # Initialise a new user into streaks with a streak count of 1 and last entry date as today.
    else:
        streaks[user_id] = (1, current_date)
        await channel.send(f"{message.author.mention}, you’ve started your streak with today's entry! 🔥")

@bot.command(aliases=["streaks"])
async def streak(message):
    '''
    Command triggered by !streak/streaks to check your own streak count.
    '''

    user_id = message.author.id
    channel = message.channel

    if user_id in streaks:
        streak_count, _ = streaks[user_id]
        if streak_count == 1:
            await channel.send(f"{message.author.mention}, you've started a streak 🔥! **{streak_count} day** logged.")
        else: 
            await channel.send(f"{message.author.mention}, your current streak 🔥 is **{streak_count} days!**")
    else:
        await channel.send(f"{message.author.mention}, you haven't started a streak yet.")

@bot.command(aliases=["lb"])
async def leaderboard(message, channel=None):
    '''
    Command triggered by !leaderboard/lb to print the current leaderboard to the channel the message was invoked.
    '''

    if channel is None:
        channel = message.channel

    await send_leaderboard(channel)

async def send_leaderboard(channel):
    '''
    Helper function that has the logic behind printing the leaderboard and is printed to the desired channel
    '''

    current_time = datetime.now(AEST)
    current_date = current_time.strftime("%d-%m-%Y")
    
    # Initial leaderboard message
    leaderboard_message = f"`{current_date}`\nCurrent leaders of the 4D Book Club 📖\n\n**Name:**\n"
    
    # Sort streaks in order of streak count and add entries to the leaderboard
    sorted_streaks = sorted(streaks.items(), key = lambda x: x[1][0], reverse=True)
    for idx, (user_id, (streak_count, _)) in enumerate(sorted_streaks, 1):
        username = bot.get_user(user_id)
        leaderboard_message += f"**{idx}.** {username.mention} - **{streak_count} days 🔥** \n"
    
    # Create the embedded message
    embedded_msg = discord.Embed(title="**⭐ 2024 Leaderboard ⭐**", description=leaderboard_message, color=discord.Color.green())

    # Send the message to the channel
    await channel.send(embed=embedded_msg)

@tasks.loop(minutes=1)
async def announce_leaderboard():
    '''
    Task that the bot will execute at 8am everyday. 
    Send the leaderboard to the #leaderboard channel every morning by invoking helper fuction send_leaderboard
    '''

    # Get current time (YYYY-MM-DD HH:MM:SS.mmmmm)
    current_time = datetime.now(AEST)

    # Send leaderboard at 8am everyday
    if current_time.hour == 8 and current_time.minute == 0:

        # Leaderboard text channel
        leaderboard_channel = bot.get_channel(1286228895858819134)
        
        # Goodmorning message
        gm_message = "@everyone Goodmorning everyone!"
        await leaderboard_channel.send(gm_message)

        # Send the message to the channel
        await send_leaderboard(leaderboard_channel)
        
@tasks.loop(minutes=1)
async def check_deadline():
    '''
    Task that the bot will execute at 10pm everyday.
    It checks to see if there are users with streaks that have not entered their daily chapter entry.
    It will remind them that they should enter the entry or else their streak count will be reset to 0.
    '''

    current_date = datetime.now(AEST).date()
    current_time = datetime.now(AEST)

    # general text channel    
    channel = bot.get_channel(1278334025639133238)

    # Checks if there are users with 0 entries and deletes them off streaks. 
    # This way, people with a streak of 0 are not pinged for this reminder.
    for user_id, (streak_count, last_entry_date) in list(streaks.items()):
        if streak_count == 0:
            streaks.pop(user_id)
            continue 
        
        # Remind them that they have two hours left before losing their streak
        if current_date == last_entry_date + timedelta(days=1):
            if current_time.hour == 22 and current_time.minute == 0:
                username = bot.get_user(user_id)
                if username:
                    await channel.send(f"{username.mention}, submit your chapter entry within 2 HOURS to keep your {streak_count} days streak alive! ❤️‍🩹 ")

        # Reset Streaks only at midnight (12:00AM)
        if current_time.hour == 0 and current_time.minute == 0 and current_date > last_entry_date + timedelta(days=1):
                streaks[user_id] = (0, last_entry_date)
                username = bot.get_user(user_id)
                if username:
                    await channel.send(f"{username.mention}, you forgot to submit your chapter entry and lost your streak of {streak_count} days! 😢")
            
bot.run(DISCORD_TOKEN)