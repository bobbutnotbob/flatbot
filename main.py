import os
import sys
import json
import traceback
import discord
import aiosqlite
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
DATABASEDIR = os.getenv('DATABASE_LOCATION')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.all()
bot = discord.Bot(debug_guilds=[GUILD], allowed_mentions=discord.AllowedMentions(users=True,roles=True,everyone=True), intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    print('----------')
  
# Load extensions/cogs
bot.load_extension('cogs.banking_cog')
# bot.load_extension('cogs.shopping_cog') -- Disabled for now

bot.run(TOKEN)
