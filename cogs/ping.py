import discord
from discord.ext import commands
from discord.ui import Button, View

from utils.safe_send import safe_send
from functions.setup_functions import set_server_setting, is_ping_cd_channel_set, is_bot_setup, load_config, is_staff_role_set


from datetime import datetime, timedelta

# cooldowns_auto = {guild_id: {"giveaway": datetime, "gameshow": datetime}}
cooldowns_auto = {}


class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    

    @commands.command()
    async def ping(self, ctx):
        
        config = load_config(ctx.guild.id)
        staff_role_id = config.get("staff_role_id") 
        
        found = False
        print("staff role id:", staff_role_id)
        for role in ctx.author.roles:
            print("role", role.id, role.name)
            if role.id == staff_role_id:
                print("found", role.id, role.name)
                found = True
                break
        if found == False:
            await safe_send(ctx, 'you aint staff')
            return
        
        view = PingButtonView(author_id=ctx.author.id)

        await ctx.send(view=view)
        

        

# Define the button handler class
class PingButtonView(View):
    def __init__(self, author_id):
        super().__init__(timeout=None)  # Keeps buttons active
        self.author_id = author_id

        button_labels = ["Giveaway", "Gameshow"]
        for label in button_labels:
            self.add_item(PingButton(label=label, author_id=author_id))



class PingButton(Button):
    def __init__(self, label, author_id):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.author_id = author_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("You can't use this button", ephemeral=True)
            return

        if self.label == "Giveaway":
            await handle_giveaway(interaction)
        else:
            await handle_gameshow(interaction)



import asyncio

async def handle_giveaway(interaction: discord.Interaction):
    config = load_config(interaction.guild.id)
    giveaway_manager_role_id = config.get("giveaway_manager_role_id") 
    giveaway_ping_role_id = config.get("giveaway_ping_role_id") 
    #giveaway_channel_id = config.get("giveaway_channel_id")
    noreq_channel_name = "・🎉┋no-req"
    giveaway_channel_name = "・🎉┋giveaway"
    ping_cd = config.get("ping_cd")
    
    if not giveaway_manager_role_id:
        await interaction.response.send_message('Giveaway manager role is not set. Set it with m!set_giveaway_manager_role', ephemeral=True)
        asyncio.create_task(interaction.message.delete())
        return

    if not any(role.id == giveaway_manager_role_id for role in interaction.user.roles):
        await interaction.response.send_message('You aint a giveaway manager', ephemeral=True)
        asyncio.create_task(interaction.message.delete())
        return
    
    if (interaction.channel.name != giveaway_channel_name and interaction.channel.name != noreq_channel_name):
        await interaction.response.send_message('Try again in the giveaway channel boy', ephemeral=True)
        #print("its", interaction.channel.name, "and u need", giveaway_channel_name)
        asyncio.create_task(interaction.message.delete())
        return
    
    if ping_cd == "True":
        await interaction.response.send_message('❌ There is currently a manual ping cooldown going on (set by staff)', ephemeral=True)
        return

    now = datetime.utcnow()
    guild_id = interaction.guild.id

    if guild_id not in cooldowns_auto:
        cooldowns_auto[guild_id] = {}

    last_ping = cooldowns_auto[guild_id].get("giveaway")
    if last_ping and now - last_ping < timedelta(minutes=30):
        remaining = timedelta(minutes=30) - (now - last_ping)
        await interaction.response.send_message(
            f'❌ Giveaway ping is on automatic cooldown. Try again in {int(remaining.total_seconds() // 60)} minutes.',
            ephemeral=True
        )
        asyncio.create_task(interaction.message.delete())
        return

    # Update cooldown
    cooldowns_auto[guild_id]["giveaway"] = now



    role = interaction.guild.get_role(giveaway_ping_role_id)
    await interaction.response.send_message(
        content=f"{role.mention}",
        allowed_mentions=discord.AllowedMentions(roles=True)
    )


    asyncio.create_task(interaction.message.delete())
    



async def handle_gameshow(interaction: discord.Interaction):
    config = load_config(interaction.guild.id)
    gameshow_host_role_id = config.get("gameshow_host_role_id") 
    gameshow_ping_role_id = config.get("gameshow_ping_role_id") 
    #gameshow_channel_id = config.get("gameshow_channel_id")
    gameshows_channel_name = "・⭐┋gameshows"
    ping_cd = config.get("ping_cd")
    
    if not gameshow_host_role_id:
        await interaction.response.send_message('Gameshow host role is not set. Set it with m!set_gameshow_host_role', ephemeral=True)
        asyncio.create_task(interaction.message.delete())
        return

    if not any(role.id == gameshow_host_role_id for role in interaction.user.roles):
        await interaction.response.send_message('You aint a gameshow host', ephemeral=True)
        asyncio.create_task(interaction.message.delete())
        return
    
    if (interaction.channel.name != gameshows_channel_name):
        await interaction.response.send_message('Try again in the gameshow channel boy', ephemeral=True)
        asyncio.create_task(interaction.message.delete())
        return
    
    if ping_cd == "True":
        await interaction.response.send_message('❌ There is currently a manual ping cooldown going on (set by staff)', ephemeral=True)
        return

    now = datetime.utcnow()
    guild_id = interaction.guild.id

    if guild_id not in cooldowns_auto:
        cooldowns_auto[guild_id] = {}

    last_ping = cooldowns_auto[guild_id].get("gameshow")
    if last_ping and now - last_ping < timedelta(minutes=30):
        remaining = timedelta(minutes=30) - (now - last_ping)
        await interaction.response.send_message(
            f'❌ Gameshow ping is on automatic cooldown. Try again in {int(remaining.total_seconds() // 60)} minutes.',
            ephemeral=True
        )
        asyncio.create_task(interaction.message.delete())
        return

    # Update cooldown
    cooldowns_auto[guild_id]["gameshow"] = now


    role = interaction.guild.get_role(gameshow_ping_role_id)
    await interaction.response.send_message(
        content=f"{role.mention}",
        allowed_mentions=discord.AllowedMentions(roles=True)
    )


    asyncio.create_task(interaction.message.delete())




async def setup(bot):
    await bot.add_cog(Ping(bot))