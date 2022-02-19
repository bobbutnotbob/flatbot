import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.group(name='sl', invoke_without_command=True)
async def shopping_list(ctx):
    await ctx.send('parent')

@shopping_list.command(name='help')
async def shopping_help(ctx):
    await ctx.send('I don\'t work for whatever reason')

@shopping_list.command(name='add')
async def add_to_shopping_list(ctx, *, item):
    with open('shopping_list.txt', 'r+') as shopping_list:
        lc = len(shopping_list.readlines()) + 1
        regular_syntax = f'{lc}. {item}\n'
        md_syntax = f'- [] {lc}. {item}\n'
        shopping_list.write(regular_syntax)

    await ctx.send(f'+ Added `{item}` to the shopping list')
    
@shopping_list.command(name='remove')
async def add_to_shopping_list(ctx, line_to_rm: int):
    with open('shopping_list.txt', 'r') as shopping_list:
        lines = shopping_list.readlines()

    index = 1
    new_line_num = 0
    with open('shopping_list.txt', 'w') as new_shopping_list:
        for line in lines:
            print(line, index)
            if index == line_to_rm:
                item = line[3:]

            else:
                new_line_num += 1
                line = line[3:]
                new_shopping_list.write(f'{new_line_num}. {line}')

            index += 1
                
    await ctx.send(f'— Removed `{item}` from the shopping list')
            
@shopping_list.command(name='clear')
async def clear_shopping_list(ctx):
    with open('shopping_list.txt', 'w') as shopping_list:
        shopping_list.write('')

    await ctx.send('Cleared the shopping list')

@shopping_list.command(name='print')
async def add_to_shopping_list(ctx):
    await ctx.send('I am the shopping list')

bot.run(TOKEN)