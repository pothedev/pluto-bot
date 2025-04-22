import discord
from discord.ext import commands
from functions.setup_functions import load_config
from variables import thumbs_middle_emoji, thumbs_down_emoji, thumbs_up_emoji, under_review_icon, approved_icon, disapproved_icon
from utils.safe_send import safe_send



class AutoSuggestion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message):

        if not message.guild:
            return

        config = load_config(message.guild.id)
        suggestions_channel_id = config.get("suggestions_channel_id")

        if message.author == self.bot.user:
            return

        if message.channel.id == suggestions_channel_id:
            embed = discord.Embed(
                description=message.content,
                color=discord.Color.yellow()
            )

            embed.set_footer(
                text=f"{message.author}  •  {message.created_at.strftime('%m/%d/%Y %I:%M %p')}",
                icon_url=message.author.display_avatar.url
            )

            embed.set_author(
                name="Suggestion「 Under Review 」",
                icon_url=under_review_icon
            )

            sent = await message.channel.send(embed=embed)

            await sent.add_reaction(thumbs_up_emoji)
            await sent.add_reaction(thumbs_middle_emoji)
            await sent.add_reaction(thumbs_down_emoji)

            await message.delete()

        # 👇 Must be outside the suggestion channel check
        await self.bot.process_commands(message)
    



class SuggestionStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

  
    @commands.command()
    async def suggestion_status(self, ctx, message_id: int, status: str, *, note: str = None):

        config = load_config(ctx.guild.id)

        suggestions_channel_id = config.get("suggestions_channel_id")
        if not suggestions_channel_id:
            return

        
        try:
            channel = self.bot.get_channel(suggestions_channel_id)
            message = await channel.fetch_message(message_id)

            if not message.embeds:
                return await ctx.send("❌ That message has no embed.")

            embed = message.embeds[0]  # Get the first embed

            if status.lower() == "approved":
                embed.color = discord.Color.green()
                icon = approved_icon
                title = "Approved"
            elif status.lower() == "disapproved":
                embed.color = discord.Color.red()
                icon = disapproved_icon
                title = "Disapproved"
            else:
                return await ctx.send("❌ Status must be `approved` or `disapproved`.")

            # Build the updated header
            if note:
                header = f"{title}「 {note} 」"
            else:
                header = f"{title}"

            embed.set_author(name=header, icon_url=icon)

            await message.edit(embed=embed)
            await safe_send(ctx, "✅ Suggestion status updated.")

        except discord.NotFound:
            await safe_send(ctx, "❌ Message not found. Make sure the ID is from this channel.")
        except discord.Forbidden:
            await safe_send(ctx, "❌ I don't have permission to edit that message.")
        except discord.HTTPException:
            await safe_send(ctx, "❌ Failed to update the message.")



