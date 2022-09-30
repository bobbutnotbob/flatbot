import os
import sys
import traceback
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = discord.Bot(debug_guilds=[798358772996243457])

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

# -------------------------------------- #
#        Shopping List Commands          #
# -------------------------------------- #

shopping_list = bot.create_group('shopping-list', 'Shopping list commands')

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
async def print(ctx):
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



# ----------------------------------- #
#           Error Handling            #
# ----------------------------------- #
bot.run(TOKEN)