from discord.ext import commands

AUTHORIZED_USERS_ID = [925728307968872509]

# def is_authorized_user():
#     async def predicate(ctx):
#         return ctx.author.id in AUTHORIZED_USERS_ID
#     return commands.check(predicate)

def is_authorized_user(ctx):
  return ctx.author.id in AUTHORIZED_USERS_ID