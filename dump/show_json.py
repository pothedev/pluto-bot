import discord
from discord.ext import commands
from utils.safe_send import safe_send
import json

class ShowJson(commands.Cog):
    def __init__(self, bot):
        self.bot=bot
    
    @commands.command()
    async def show_json(self, ctx):
        try:
            with open("config.json", "r") as f:
                config_data = json.load(f)

            pretty_json = json.dumps(config_data, indent=2)
            if len(pretty_json) > 1900:
                await safe_send(ctx.channel, "⚠️ Config is too long to display here.")
            else:
                await safe_send(ctx.channel, f"```json\n{pretty_json}\n```")
        except Exception as e:
            await safe_send(ctx.channel, f"❌ Failed to load config: {e}")

async def setup(bot):
    await bot.add_cog(ShowJson(bot))