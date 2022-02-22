import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

# -------------------------------------- #
#        Shopping List Commands          #
# -------------------------------------- #

@bot.group(name='shopping-list', aliases=['sl'], invoke_without_command=True)
async def shopping_list(ctx):
    await ctx.send('parent')

@shopping_list.command(name='help', aliases=['h'])
async def shopping_help(ctx):
    await ctx.send('I don\'t work for whatever reason')

@shopping_list.command(name='add')
async def add_to_shopping_list(ctx, *, items):
    with open('shopping_list.txt', 'r+') as shopping_list:
        lines = shopping_list.readlines() 
        lc = len(lines) + 1
        items = items.split(',')
        for item in items:
            if item in lines:
                await ctx.send(f'`{item} ')
            else:
                item = item.strip()
                shopping_list.write(item + '\n')
                lc += 1

    await ctx.send(f'+ Added `{len(items)}` items to the shopping list')
    
@shopping_list.command(name='remove', aliases=['rm'])
async def remove_from_shopping_list(ctx, item_to_rm: int):
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
                
    await ctx.send(f'— Removed `{removed_item}` from the shopping list')
            
@shopping_list.command(name='clear')
async def clear_shopping_list(ctx):
    with open('shopping_list.txt', 'w') as shopping_list:
        shopping_list.write('')

    await ctx.send('Cleared the shopping list')

@shopping_list.command(name='print')
async def print_shopping_list(ctx):
    with open('shopping_list.txt', 'r') as shopping_list:
        data = shopping_list.readlines()
        numbered_list = ""
        for i in range(len(data)):
            numbered_line = f'{i + 1}. {data[i]}'
            numbered_list += numbered_line

    await ctx.send(f'```\n{numbered_list}```')

# ----------------------------------- #
#           Error Handling            #
# ----------------------------------- #

# --- Shopping List --- #
bot.run(TOKEN)