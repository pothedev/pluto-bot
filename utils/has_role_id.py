from discord.ext import commands

# def has_role_id(role_id):
#     async def predicate(ctx):
#         return any(role.id == role_id for role in ctx.author.roles)
#     return commands.check(predicate)


def has_role_id(role_id, ctx):
  return any(role.id == role_id for role in ctx.author.roles)
