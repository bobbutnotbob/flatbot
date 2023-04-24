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

# Payment buttons
'''
class PaymentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
self
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
'''

    
class BankingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    bank_transfer = SlashCommandGroup('bank-transfer', 'Commands related to bank transfers')
    
    # Command for creating a payment request
    @bank_transfer.command(description='Request payment from flat members')
    async def request(self, ctx, target: discord.abc.Mentionable, amount: float, description = "No description provided"):

        # Round inputted request amount to 2 decimal places, get the string required to mention the targeted user/role
        amount = round(amount, 2)
        mention_str = target.mention

        # If target is '@everyone', set the mention string to '@everyone' (mentioning the role id of @everyone freaks it out)
        if target.id == ctx.guild_id:
            mention_str = '@everyone'

        # Determines whether target is a role or a single user and populates the to_pay list accordingly
        if hasattr(target, 'members'):
            to_pay = [member.id for member in target.members]
        else:
            to_pay = [target.id]

        # Connect to the database and retrieve list of valid targets for requesting payment
        async with aiosqlite.connect(f'{DATABASEDIR}/{ctx.guild.id}.db') as db:
            async with db.execute('SELECT UserId FROM Users') as cursor:
                userlist = await cursor.fetchall()
                userlist = [user for (user,) in userlist]

                # Check whether each user in the to_pay list is a valid target
                    # If target is not valid and there are multiple targets in to_pay, remove the target from list
                    # If to_pay contains only 1 user, fail to create the payment request
                for user in to_pay:
                    # TODO: Currently provides no feedback on whether a target is valid or not. If multiple targets are removed and the payment fails, only the last target will be mentioned in the response
                    if user not in userlist:
                        if len(userlist) == 1:
                            print('Gah!')
                            await ctx.respond(f'You can\'t request a payment from <@{user}> because they do not have an entry in the database.', ephemeral=True)
                            return

                        else:
                            to_pay.remove(user)
                            print(f'Failed adding user with ID {user} as they are not in the database')

            # Respond with a text message containing the details of the payment request, and add a checkmark reaction to the message
            await ctx.respond(f'**To:** {ctx.author.mention}\n**From:** {mention_str}\n**Amount:** ${amount}\n**Description:** {description}')
            message = await ctx.interaction.original_message()
            await message.add_reaction('✅')
            
            # Commit the details of the request into the database
            await db.execute('PRAGMA foreign_keys = ON')
            query = f'INSERT INTO Payments VALUES ({message.id}, {amount}, "{description}", {ctx.author.id}, "{to_pay}", "{to_pay}")'
            await db.execute(query)
            await db.commit()

    @bank_transfer.command(description='Show a summary of outstanding payments between you and another member of the flat')
    @discord.option('target', default = None, required = False)
    async def summary(self, ctx, target: discord.User):
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
    async def createdb(self, ctx):
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

def setup(bot):
    bot.add_cog(BankingCog(bot))
    print('Loaded banking module')
