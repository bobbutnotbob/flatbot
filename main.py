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

@bot.event
async def on_raw_reaction_add(reaction):
    # If the member reacting to the message is a bot, or using an emoji we don't care about, do nothing
    if reaction.member.bot:
        return
    if str(reaction.emoji) != '✅':
        return
    
    # Set some variables from the context of the reaction
    message_id = reaction.message_id
    user_id = reaction.user_id
    reaction_channel = bot.get_channel(reaction.channel_id)   
    message = await reaction_channel.fetch_message(message_id)

    # If the message being reacted to does not already contain a reaction from the bot, return
    bot_reacted = False
    for existing_reaction in message.reactions:
        async for existing_reactor in existing_reaction.users():
            if existing_reactor.id == bot.user.id:
                bot_reacted = True
                break
    if not bot_reacted:
        return

    # Connect to db and attempt to find a payment entry for the message that is being reacted to
    async with aiosqlite.connect(f'{DATABASEDIR}/{reaction.guild_id}.db') as db:
        async with db.execute(f'SELECT RequestedFrom, UnpaidBy FROM Payments WHERE MessageId = {message_id}') as cursor:
            db_data = await cursor.fetchone()
            # If no matching payment is found, return
            if db_data == None:
                await reaction_channel.send('Unable to find payment in database')
                return
            
            # Otherwise, deserialize the 'RequestedFrom' and 'UnpaidBy' JSON from the db and store them in lists
            requested_from = json.loads(db_data[0])
            unpaid_by = json.loads(db_data[1])
            
            if user_id not in requested_from:
                response = 'You are not required to pay this'
            
            elif user_id not in unpaid_by:
                response = 'You have already payed this'

            # If all checks pass, remove the user from the 'unpaid_by' list, reserialize it and commit it back into the db
            else:
                unpaid_by.remove(user_id)
                unpaid_by = json.dumps(unpaid_by)
                await cursor.execute(f'UPDATE Payments SET UnpaidBy = "{unpaid_by}" WHERE MessageId = {message_id}')
                await db.commit()
                response = 'Successfully updated payment'
                
        await reaction_channel.send(response)

@bot.event
async def on_raw_reaction_remove(reaction):
    reaction_channel = bot.get_channel(reaction.channel_id)
    await reaction_channel.send('Bazinga!')
    return
  
# Load extensions/cogs
bot.load_extension('cogs.banking_cog')
# bot.load_extension('cogs.shopping_cog') -- Disabled for now

bot.run(TOKEN)
