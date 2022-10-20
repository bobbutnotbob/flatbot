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
        user_id = interaction.user.id
        message_id = interaction.message.id

        async with aiosqlite.connect(f'{DATABASEDIR}/{interaction.guild.id}.db') as db:
            async with db.execute(f'SELECT RequestedFrom, UnpaidBy FROM Payments WHERE MessageId = {message_id}') as cursor:
                message = await cursor.fetchone()
                print(message)
                if message == None:
                    await interaction.response.send_message('Unable to find payment in database', ephemeral=True)
                    return
                
                requested_from = json.loads(message[0])
                unpaid_by = json.loads(message[1])
                
                if user_id not in requested_from:
                    response = 'You are not required to pay this'
                
                elif user_id not in unpaid_by:
                    response = 'You have already payed this'

                else:
                    unpaid_by.remove(user_id)
                    unpaid_by = json.dumps(unpaid_by)
                    await cursor.execute(f'UPDATE Payments SET UnpaidBy = "{unpaid_by}" WHERE MessageId = {message_id}')
                    await db.commit()
                    response = 'Successfully updated payment'
                
        await interaction.response.send_message(response, ephemeral=True)

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.red, custom_id="delete_button")
    async def delete(self, button: discord.ui.Button, interaction: discord.Interaction):
        async with aiosqlite.connect(f'{DATABASEDIR}/{interaction.guild.id}.db') as db:
            async with db.execute(f'SELECT * FROM Payments WHERE MessageId = {interaction.message.id}') as cursor:
                message = await cursor.fetchone()

                if message == None:
                    response = 'Unable to find payment in database'

                elif message[3] == interaction.user.id:
                    await cursor.execute(f'DELETE FROM Payments WHERE MessageId = {interaction.message.id}')
                    await db.commit()
                    await interaction.message.delete()
                    response = 'Successfully deleted payment'

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
        to_pay = [member.id for member in target.members]
    else:
        to_pay = [target.id]
    
    async with aiosqlite.connect(f'{DATABASEDIR}/{ctx.guild.id}.db') as db:
        async with db.execute('SELECT UserId FROM Users') as cursor:
            userlist = await cursor.fetchall()
            userlist = [user for (user,) in userlist]
            for user in to_pay:
                if user not in userlist:
                    if len(userlist) == 1:
                        print('Gah!')
                        await ctx.respond(f'You can\'t request a payment from <@{user}> because they do not have an entry in the database.', ephemeral=True)
                        return
                    
                    else:
                        to_pay.remove(user)
                        print(f'Failed adding user with ID {user} as they are not in the database')

        await ctx.respond(f'**To:** {ctx.author.mention}\n**From:** {mention_str}\n**Amount:** ${amount}\n**Description:** {description}', view=PaymentView())
        message = await ctx.interaction.original_message()
        await db.execute('PRAGMA foreign_keys = ON')
        query = f'INSERT INTO Payments VALUES ({message.id}, {amount}, "{description}", {ctx.author.id}, "{to_pay}", "{to_pay}")'
        await db.execute(query)
        await db.commit()
        
@bank_transfer.command(description='Show a summary of outstanding payments between you and another member of the flat')
@discord.option('target', default = None, required = False)
async def summary(ctx, target: discord.User):
    if target == None:
        userlist = [user for user in ctx.guild.members if not user.bot]
        userlist.remove(ctx.author)

    else:
        userlist = [target]

    async with aiosqlite.connect(f'{DATABASEDIR}/{ctx.guild.id}.db') as db:
        response = ''
        for user in userlist:
            async with db.execute(f'SELECT Amount FROM Payments WHERE RequestedBy = {ctx.author.id} AND UnpaidBy LIKE "%{user.id}%"') as cursor:
                row = await cursor.fetchall()
                amounts = [amount for (amount,) in row]
                response += f'**{user.name}** has **{len(amounts)}** outstanding payments to you, totalling **${sum(amounts)}**.\n'

    await ctx.respond(response)

@bank_transfer.command(description='Creates database')
async def createdb(ctx):
    async with aiosqlite.connect(f'{DATABASEDIR}/{ctx.guild.id}.db') as db:
        await db.execute('PRAGMA foreign_keys = ON')
        with open(DATABASEDIR+'/table_schema.sql') as schema:
            await db.executescript(schema.read())

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
