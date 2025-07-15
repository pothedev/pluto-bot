import discord
from discord.ext import commands
from discord.ui import Button, View

from utils.safe_send import safe_send
from functions.setup_functions import set_server_setting, is_ping_cd_channel_set, is_bot_setup, load_config, is_staff_role_set

import time
import asyncio



cooldowns = {
    "Announcement": 15,
    "Giveaway/Gameshow": 30, 
    "Event": 30,
    "Here": 45,
    "Everyone": 1
}


async def reset_ping_cd_after(guild_id: int, delay_seconds: int, interaction, ping_cd_channel_id):
    await asyncio.sleep(delay_seconds)
    set_server_setting(guild_id, "ping_cd", "False")
    print(f"Ping cooldown reset for guild {guild_id}")
    channel = interaction.guild.get_channel(ping_cd_channel_id)
    

    

class PingCd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    

    @commands.command()
    async def ping_cd(self, ctx):
        
        config = load_config(ctx.guild.id)
        staff_role_id = config.get("staff_role_id") 

        if not is_staff_role_set(ctx.guild.id):
            await safe_send(ctx, "set staff role first with set_staff_role")
            return

        if not is_ping_cd_channel_set(ctx.guild.id):
            await safe_send(ctx, "❌ Ping CD channel is not set up. Use set_ping_cd_channel {channel}")
            return
        
        
        found = False
        print("staff role id:", staff_role_id)
        for role in ctx.author.roles:
            print("role", role.id, role.name)
            if role.id == staff_role_id:
                print("found", role.id, role.name)
                found = True
                break
        if found == False:
            await safe_send(ctx, 'boy you aint staff')
            return
        

        embed = discord.Embed(
            title="Ping Cooldown",
            description="Choose a type of ping to log ping cooldown for",
            color=discord.Color.blue()
        )

        # Create a View with 5 buttons
        view = PingButtonView()

        await ctx.send(embed=embed, view=view)


# Define the button handler class
class PingButtonView(View):
    def __init__(self):
        super().__init__(timeout=None)  # Keeps buttons active

        button_labels = ["Announcement", "Event", "Giveaway/Gameshow", "Here", "Everyone"]
        for label in button_labels:
            self.add_item(PingButton(label=label))


class PingButton(Button):
    def __init__(self, label):
        super().__init__(label=label, style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        await handle_button(interaction, self.label)


# Shared handler function
async def handle_button(interaction: discord.Interaction, label: str):
    await interaction.response.send_message(f"🔔 You chose: **{label}**", ephemeral=True)

    if is_bot_setup(interaction.guild.id):

        config = load_config(str(interaction.guild.id))
        ping_cd_channel_id = config.get("ping_cd_channel_id")

        # Get the channel object from the ID
        channel = interaction.guild.get_channel(ping_cd_channel_id)

        if channel is None:
            await interaction.followup.send("⚠️ Ping cooldown channel not found.", ephemeral=True)
            return

        minutes = cooldowns.get(label, 10)  # default 10 minutes if not found
        future_ts = int(time.time()) + minutes * 60
        formatted = f"<t:{future_ts}:R>"  # e.g., "in 10 minutes"
        formatted1 = f"<t:{future_ts}:t>"  # e.g., "in 10 minutes"

        embed = discord.Embed(
            title="Ping Cooldown",
            description=f"🔕 Ping cooldown is over {formatted} at {formatted1}",
            color=discord.Color.blue()
        )

        set_server_setting(interaction.guild.id, "ping_cd", "True")
        
        await channel.send(embed=embed)
        await channel.send("@here")

        # Start async background task to reset cooldown
        asyncio.create_task(reset_ping_cd_after(interaction.guild.id, minutes * 60, interaction, ping_cd_channel_id))




async def setup(bot):
    await bot.add_cog(PingCd(bot))