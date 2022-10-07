import os
import sys
import json
import traceback
import discord
import aiosqlite
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
bot = discord.Bot(debug_guilds=[798358772996243457], allowed_mentions=discord.AllowedMentions(users=True,roles=True,everyone=True), intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

# Intitialise command groups
shopping_list = bot.create_group('shopping-list', 'Shopping list commands')
bank_transfer = bot.create_group('bank-transfer', 'Commands for managing bank transfers')

# -------------------------------------- #
#        Shopping List Commands          #
# -------------------------------------- #

@shopping_list.command(description='Display bot help')
async def help(ctx):
    await ctx.respond('I don\'t work for whatever reason')

@shopping_list.command(description='Add an item to the shopping list')
async def add(ctx, *, items):
    with open('shopping_list.txt', 'r+') as shopping_list:
        lines = shopping_list.readlines() 
        lc = len(lines) + 1
        print(items, lines)
        for item in items:
            if item in lines:
                await ctx.respond(f'`{item} ')
            else:
                item = item.strip()
                shopping_list.write(item + '\n')
                lc += 1

    await ctx.respond(f'+ Added `{len(items)}` items to the shopping list')
    
@shopping_list.command(description='Remove an item from the shopping list')
async def remove(ctx, item_to_rm: int):
    with open('shopping_list.txt', 'r') as sl_read:
        shopping_list = sl_read.readlines()

    index = 1
    with open('shopping_list.txt', 'w') as sl_write:
        for item in shopping_list:
            if index == item_to_rm:
                removed_item = item
                pass

            else:
                sl_write.write(item)

            index += 1
                
    await ctx.respond(f'— Removed `{removed_item}` from the shopping list')
            
@shopping_list.command(description='Clear the shopping list')
async def clear(ctx):
    with open('shopping_list.txt', 'w') as shopping_list:
        shopping_list.write('')

    await ctx.respond('Cleared the shopping list')

@shopping_list.command(description='Print the shopping list')
async def show(ctx):
    with open('shopping_list.txt', 'r') as shopping_list:
        data = shopping_list.readlines()
        numbered_list = ""
        for i in range(len(data)):
            numbered_line = f'{i + 1}. {data[i]}'
            numbered_list += numbered_line

    await ctx.respond(f'```\n{numbered_list}```')

# -------------------------------------- #
#        Bank Transfer Commands          #
# -------------------------------------- #

@bank_transfer.command(description='Request payment from flat members')
async def request(ctx, target: discord.abc.Mentionable, amount: float):
    mention_str = target.mention
    if target.id == ctx.guild_id:
        mention_str = '@everyone'
        
    await ctx.respond(f'Requested **${amount}** from {mention_str}.')

@bank_transfer.command(description='Show a summary of outstanding payments between you and another member of the flat')
async def summary(ctx, target: discord.User):
    user_id = target.id
    async with aiosqlite.connect('database/database_test.db') as db:
        await db.execute('PRAGMA foreign_keys = ON;')
        async with db.execute(f'SELECT Amount FROM Outstanding WHERE RequestedBy = {ctx.author.id} AND PaidBy NOT LIKE "%{target.id}%"') as cursor:
            row = await cursor.fetchall()

        amounts = [ amount for (amount,) in row ]

    await ctx.respond(f'**{target.name}** has **{len(amounts)}** outstanding payments to you, totalling **${round(sum(amounts), 2)}**.')

@bank_transfer.command(description='Testing')
async def sqltest(ctx):
    userlist = ctx.guild.members
    async with aiosqlite.connect('database/database_test.db') as db:
        await db.execute('PRAGMA foreign_keys = ON;')
        for user in userlist:
            print(user.id)
            await db.execute(f'INSERT INTO Users (UserId) VALUES ({user.id}) ON CONFLICT DO NOTHING')
        await db.commit()
    
        async with db.execute(f'SELECT * FROM Users') as cursor:
            row = await cursor.fetchall()
    
    await ctx.respond(f'Users: {row}')

# ----------------------------------- #
#           Error Handling            #
# ----------------------------------- #
bot.run(TOKEN)
