import discord

bot = discord.Bot(debug_guilds=[798358772996243457]) # specify the guild IDs in debug_guilds

# create slash command group with bot.create_group
greetings = bot.create_group("greetings", "Greet people")
pineapple = bot.create_group("pineapple", "Test group")

@greetings.command()
async def hello(ctx):
  await ctx.respond(f"Hello, {ctx.author}!")

@greetings.command(description='desciption')
async def bye(ctx, number: int):
  await ctx.respond(f"Bye, {ctx.author}! {number}")

@pineapple.command(description='yim yum')
async def bye(ctx, food: str):
  await ctx.respond(f"{food} is a yummy food!")

bot.run('OTQyOTY4NTIwNjYzMjQwNzI0.GXls0P.tGMn9FyjGxm8IfHXUgCWfF6ylbHP6BYs4Y6VXY')