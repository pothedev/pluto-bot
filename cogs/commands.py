import discord
from discord.ext import commands
from utils.safe_send import safe_send



class Commands(commands.Cog):

  def __init__(self, bot):
     self.bot = bot

  @commands.command(name="commands")
  async def cmds(self, ctx):
      commands = (
          "➖ update {role} {all/member}\n"
          "➖ set_booster_role\n"
          "➖ set_logs_channel\n"
          "➖ set_bloxlink_key\n"
          "➖ set_trello_key\n"
          "➖ set_trello_token\n"
          "➖ set_trello_board_id\n"
          "➖ set_trello_list_id\n"
          "➖ setup_status\n"
          "➖ setup\n"
      )

      embed = discord.Embed(
          title="🛠️  Available commands",
          color=discord.Color.dark_gray()
      )

      embed.add_field(name="\u200b", value=commands, inline=False)
      await safe_send(ctx.channel, embed=embed)



async def setup(bot):
    await bot.add_cog(Commands(bot))