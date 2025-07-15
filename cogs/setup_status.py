from discord.ext import commands
from discord.ui import Button, View

from utils.safe_send import safe_send
from functions.setup_functions import is_bot_setup

class SetUpStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command
    def setup_status(ctx):
        is_setup = is_bot_setup(ctx)
        if is_setup:  
          safe_send(ctx, "✅ The bot is set up")
        else:
          safe_send(ctx, "❌ The bot is not set up")

async def setup(bot):
    await bot.add_cog(SetUpStatus(bot)) 