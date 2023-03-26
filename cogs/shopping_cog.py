import os
import json
import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup
import aiosqlite
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
DATABASEDIR = os.getenv('DATABASE_LOCATION')
GUILD = os.getenv('DISCORD_GUILD')

class ShoppingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    shopping_list = SlashCommandGroup('shopping-list', 'Commands related to the shopping list')

    @shopping_list.command(description='Add an item to the shopping list')
    async def add(self, ctx, *, items):
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
    async def remove(self, ctx, item_to_rm: int):
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
    async def clear(self, ctx):
        with open('shopping_list.txt', 'w') as shopping_list:
            shopping_list.write('')
    
        await ctx.respond('Cleared the shopping list')
    
    @shopping_list.command(description='Print the shopping list')
    async def show(self, ctx):
        with open('shopping_list.txt', 'r') as shopping_list:
            data = shopping_list.readlines()
            numbered_list = ""
            for i in range(len(data)):
                numbered_line = f'{i + 1}. {data[i]}'
                numbered_list += numbered_line
    
        await ctx.respond(f'```\n{numbered_list}```')
        
def setup(bot):
    bot.add_cog(ShoppingCog(bot))
    print('Loaded shopping module')
