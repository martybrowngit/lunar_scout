import discord
import ephem
import datetime
import pytz
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext import commands
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv

# Replace with your own bot token
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Your city's latitude and longitude (example: Adelaide)
LAT = '-34.9285'
LON = '138.6007'

# Channel ID to send messages to
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", "0"))

# Setup bot
intents = discord.Intents.default()

intents.message_content = True # This hopefully fixes populates the content of the message lol

bot = commands.Bot(command_prefix="!", intents=intents)
scheduler = AsyncIOScheduler()


def get_moon_phase():
    obs = ephem.Observer()
    obs.lat = LAT
    obs.lon = LON
    obs.date = datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S")
    moon_phase = ephem.Moon(obs).phase
    return moon_phase

def is_full_moon_today():
    return get_moon_phase() >= 98

async def check_full_moon():
    if is_full_moon_today():
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            await channel.send("🌕 It's a full moon tonight!")

@bot.command(name="moon")
async def moon_command(ctx):
    phase = get_moon_phase()
    if is_full_moon_today():
        await ctx.send("🌕 Yes! Tonight is a full moon.")
    elif phase <= 2:
        await ctx.send("🌑 It's a new moon tonight.")
    else:
        await ctx.send(f"🌙 The moon phase today is **{phase:.1f}% illuminated**.")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    scheduler.start()

    # Adelaide timezone
    adelaide_tz = pytz.timezone("Australia/Adelaide")

    # Schedule the daily full moon check (UTC 10:00am example)
    scheduler.add_job(
        check_full_moon, 
        trigger=CronTrigger(hour=9, minute=0, timezone=adelaide_tz),
        id="full_moon_job",
        replace_existing=True)

bot.run(TOKEN)
