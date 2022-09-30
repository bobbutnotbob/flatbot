import os
import sys
import traceback
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = discord.Bot()

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
        print("Hello!")
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

# -------------------------------------- #
#        Bank Transfer Commands          #
# -------------------------------------- #



# ----------------------------------- #
#           Error Handling            #
# ----------------------------------- #
'''
# --- Main Handler --- #
@bot.event
async def on_command_error(ctx, error):
    
    # Prevent errors being handled that should be handled locally
    if hasattr(ctx.command, 'on_error'):
            return    

    ignored = (commands.CommandNotFound, )

        # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        error = getattr(error, 'original', error)

        # Anything in ignored will return and prevent anything happening.
        if isinstance(error, ignored):
            return

        if isinstance(error, commands.DisabledCommand):
            await ctx.send(f'{ctx.command} has been disabled.')

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except discord.HTTPException:
                pass

        # For this error example we check to see where it came from...
        elif isinstance(error, commands.BadArgument):
            if ctx.command.qualified_name == 'tag list':  # Check if the command being invoked is 'tag list'
                await ctx.send('I could not find that member. Please try again.')

        else:
            # All other Errors not returned come here. And we can just print the default TraceBack.
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
'''

# --- Shopping List --- #
bot.run(TOKEN)