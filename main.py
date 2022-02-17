import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

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
        md_syntax = f'- [] {lc}. {item}\n'
        shopping_list.write(md_syntax)

    await ctx.send(f'+ Added `{item}` to the shopping list')

@shopping_list.command(name='remove')
async def add_to_shopping_list(ctx, line_to_rm: int):
    index = 1
    with open('shopping_list.txt', 'r') as shopping_list:
        lines = shopping_list.readlines()
    with open('shopping_list.txt', 'w') as new_shopping_list:
        for line in lines:
            if index == line_to_rm:
                item = line[8:]
                continue
            else:
                shopping_list.write(line)
    
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