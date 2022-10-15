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
    
# Payment buttons
class PaymentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Pay", style=discord.ButtonStyle.green, custom_id="pay_button")
    async def pay(self, button: discord.ui.Button, interaction: discord.Interaction):
        async with aiosqlite.connect(f'{DATABASEDIR}/{interaction.guild.id}.db') as db:
            message = await db.execute_fetchall(f'SELECT * FROM Payments WHERE MessageId = {interaction.message.id}')

        await interaction.response.send_message(f'ID of message is {interaction.message.id}', ephemeral=True)

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.red, custom_id="delete_button")
    async def delete(self, button: discord.ui.Button, interaction: discord.Interaction):
        async with aiosqlite.connect(f'{DATABASEDIR}/{interaction.guild.id}.db') as db:
            message = await db.execute_fetchall(f'SELECT * FROM Payments WHERE MessageId = {interaction.message.id}')
            if not message:
                message = None
            else:
                message = message[0]
            
            if message == None:
                response = 'Unable to find payment in database'

            elif message[3] == interaction.user.id:
                await db.execute(f'DELETE FROM Payments WHERE MessageId = {interaction.message.id}')
                await interaction.message.delete()
                response = 'Successfully deleted payment'
                await db.commit()

            else:
                response = 'You do not have permission to delete this payment'
        
        await interaction.response.send_message(response, ephemeral=True)
    
    # Select * From Outstanding Where Id = interaction.Message.id
    # json.dumps('ToPay')
    # pop(user.id)
    # json.loads
    # update record in db

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
async def request(ctx, target: discord.abc.Mentionable, amount: float, description = "No description provided"):
    amount = round(amount, 2)
    mention_str = target.mention

    if target.id == ctx.guild_id:
        mention_str = '@everyone'
    
    if hasattr(target, 'members'):
        to_pay = json.dumps([member.id for member in target.members])
    else:
        to_pay = json.dumps([target.id])
    
    await ctx.respond(f'**To:** {ctx.author.mention}\n**From:** {mention_str}\n**Amount:** ${amount}\n**Description:** {description}', view=PaymentView())
    message = await ctx.interaction.original_message()

    async with aiosqlite.connect(f'{DATABASEDIR}/{ctx.guild.id}.db') as db:
        await db.execute('PRAGMA foreign_keys = ON;')
        query = f'INSERT INTO Payments (MessageId, Amount, RequestedBy, UnpaidBy) VALUES ({message.id}, {amount}, {ctx.author.id}, "{to_pay}")'
        print(query)
        await db.execute(query)
        await db.commit()
        
@bank_transfer.command(description='Show a summary of outstanding payments between you and another member of the flat')
async def summary(ctx, target: discord.User):
    user_id = target.id
    async with aiosqlite.connect(f'{DATABASEDIR}/{ctx.guild.id}.db') as db:
        await db.execute('PRAGMA foreign_keys = ON;')
        async with db.execute(f'SELECT Amount FROM Outstanding WHERE RequestedBy = {ctx.author.id} AND PaidBy NOT LIKE "%{target.id}%"') as cursor:
            row = await cursor.fetchall()

        amounts = [ amount for (amount,) in row ]

    await ctx.respond(f'**{target.name}** has **{len(amounts)}** outstanding payments to you, totalling **${sum(amounts)}**.')

@bank_transfer.command(description='Creates database')
async def createdb(ctx):
    async with aiosqlite.connect(f'{DATABASEDIR}/{ctx.guild.id}.db') as db:
        await db.execute('PRAGMA foreign_keys = ON;')
        with open(DATABASEDIR+'/table_schema.sql') as schema:
            try:
                await db.executescript(schema.read())
            except aiosqlite.Error as err:
                print(err)
        userlist = ctx.guild.members
        for user in userlist:
            if user.bot:
                continue

            print(user.id)
            await db.execute(f'INSERT INTO Users (UserId) VALUES ({user.id}) ON CONFLICT DO NOTHING')
        await db.commit()
    
    await ctx.respond(f'Updated database')

# ----------------------------------- #
#           Error Handling            #
# ----------------------------------- #
bot.run(TOKEN)
