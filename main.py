import discord
from discord.ext import commands

from functions.append_user import append_booster
from functions.get_username import get_username
from functions.get_cards import get_cards
from functions.remove_user import remove_booster
from functions.setup_functions import *
from functions.keepalive import keep_alive

from dotenv import load_dotenv
import os

from functions.firebase_config import db


load_dotenv() 

BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")


keep_alive()  # start the fake server 



intents = discord.Intents.default()
intents.message_content = True
intents.members = True  

prefix = "m!"

bot = commands.Bot(command_prefix=prefix, intents=intents)

CONFIG_FILE = "./config.json"



async def safe_send(channel, message=None, *, embed=None):
    try:
        # If message is a string, treat it as content
        if isinstance(message, str):
            await channel.send(content=message, embed=embed)
        elif embed:
            await channel.send(embed=embed)
        else:
            print("[Warning] safe_send called with neither content nor embed.")
    except discord.Forbidden:
        print(f"[Permission Error] Cannot send to channel: {channel}")
    except discord.HTTPException as e:
        print(f"[Discord Error] {e}")





def is_duplicate(label, guild_id):
  labels = get_cards(guild_id)[1]
  if label in labels:
    return True
  else:
    return False




@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")




#---------------------- manual update commands -------------------------

@bot.command()
async def update(ctx, role_arg: str, amount_arg: str):
    if not is_bot_setup(ctx.guild.id):
        await safe_send(ctx.channel, "❌ Bot is not fully set up. Use `m!setup_status` to check what’s missing.")
        return
    
    config = load_config(str(ctx.guild.id))
    
    logs_channel_id = config["logs_channel_id"]
    booster_role_id = config["booster_role_id"]
    logs_channel = ctx.guild.get_channel(int(logs_channel_id))

    if role_arg.lower() != "booster":
        await safe_send(ctx.channel, "Invalid role. Only `booster` is supported.")
        return

    guild = ctx.guild
    if not guild:
        await safe_send(ctx.channel, "Server not found.")
        return

    booster_role = discord.utils.get(guild.roles, id=int(booster_role_id))
    if not booster_role:
        await safe_send(ctx.channel, "Booster role not found.")
        return

    #update all boosters
    if amount_arg.lower() == "all":
        await safe_send(logs_channel, "Bulk booster update was triggered")
        updated = 0
        skipped = 0
        for member in booster_role.members: 
            discord_id = str(member.id)
            roblox_user = get_username(discord_id, str(ctx.guild.id))
            if roblox_user:
                if not is_duplicate(roblox_user, str(ctx.guild.id)):
                    append_booster(roblox_user, str(ctx.guild.id))
                    updated += 1
                    await safe_send(logs_channel, f"✅ User {member} was added to the booster list as {roblox_user}.")
                else:
                    await safe_send(logs_channel, f"⚠️ User {member} is already in the booster list as {roblox_user}. Skipped.")
            else:
                await safe_send(logs_channel, f"❌ Roblox username was not found for {member}.")
                skipped += 1
        message = ""
        if skipped == 1:
            message = f"Didn't find roblox account for {skipped} booster"
        elif skipped > 0:
            message = f"Didn't find roblox account for {skipped} booster"
        await safe_send(ctx.channel, f"✅ Booster list updated for {updated} boosters. {message}")
        await safe_send(logs_channel, f"✅ Booster list updated for {updated} boosters. {message}")
        return

    #update a specific user
    target_member = None
    if ctx.message.mentions:
        target_member = ctx.message.mentions[0]
    else:
        try:
            target_member = await commands.MemberConverter().convert(ctx, amount_arg)
        except:
            await safe_send(ctx.channel, "❌ Couldn't find the specified user.")
            return

    if booster_role not in target_member.roles:
        await safe_send(ctx.channel, "❌ This user doesn't have the booster role.")
        return

    discord_id = str(target_member.id)
    try:
        roblox_user = get_username(discord_id, str(ctx.guild.id))
        if roblox_user:
            if not is_duplicate(roblox_user, str(ctx.guild.id)):
                append_booster(roblox_user, str(ctx.guild.id))
                await safe_send(ctx.channel, f"✅ User {target_member} was added to the booster list as {roblox_user}.")
                await safe_send(logs_channel, f"✅ User {target_member} was added to the booster list as {roblox_user}.")
            else:
                await safe_send(ctx.channel, f"⚠️ User {target_member} is already in the booster list as {roblox_user}.")
        else:
            await safe_send(ctx.channel,"❌ Roblox username not found.")
    except Exception as e:
        print(f"Error updating {discord_id}: {e}")
        await safe_send(ctx.channel, "❌ Something went wrong while updating.")



#--------------------- auto commands ------------------------

@bot.event
async def on_member_update(before, after):
    if is_bot_setup(after.guild.id):
        config = load_config(str(after.guild.id))

        booster_role_id = config["booster_role_id"]
        logs_channel_id = config["logs_channel_id"]
        booster_role = discord.utils.get(after.guild.roles, id=int(booster_role_id))
        logs_channel = after.guild.get_channel(int(logs_channel_id))
        
        if not booster_role:
            print("Booster role not found.")
            return

        had_booster = booster_role in before.roles
        has_booster = booster_role in after.roles

        discord_id = str(after.id)
        roblox_user = get_username(discord_id, str(after.guild.id))

        #auto add
        if not had_booster and has_booster:
            if roblox_user:
                if not is_duplicate(roblox_user, str(after.guild.id)):
                    append_booster(roblox_user, str(after.guild.id))
                    if logs_channel:
                        await safe_send(logs_channel, f"✅ {after.mention} boosted the server and was added to Trello as **{roblox_user}**.")
                else:
                    if logs_channel:
                        await safe_send(logs_channel, f"⚠️ {after.mention} boosted the server but is already in the Trello list as **{roblox_user}**.")
            else:
                if logs_channel:
                    await safe_send(logs_channel, f"⚠️ {after.mention} boosted the server. Roblox username not found.")

        #auto remove
        elif had_booster and not has_booster:
            if roblox_user:
                remove_booster(roblox_user, str(after.guild.id))
                if logs_channel:
                    await safe_send(logs_channel, f"✅ {after.mention} unboosted the server and was removed from Trello as **{roblox_user}**.")
            else:
                if logs_channel:
                    await safe_send(logs_channel, f"⚠️ {after.mention} unboosted the server. Roblox username not found.")



# --------------------------------- SET UP -----------------------------------


@bot.command()
async def set_booster_role(ctx, role: discord.Role):
    if role in ctx.guild.roles:
        set_server_setting(ctx.guild.id, "booster_role_id", role.id)
        await safe_send(ctx.channel, f"✅ Booster role set to {role.name}.")
    else:
        await safe_send(ctx.channel, "❌ Role not found in this server.")

@bot.command()
async def set_logs_channel(ctx, channel: discord.TextChannel):
    if channel in ctx.guild.text_channels:
        set_server_setting(ctx.guild.id, "logs_channel_id", channel.id)
        await safe_send(ctx.channel, f"✅ Logs channel set to {channel.mention}.")
    else:
        await safe_send(ctx.channel, "❌ Channel not found in this server.")

@bot.command()
async def set_bloxlink_key(ctx, key: str):
    if len(key) > 10:
        set_server_setting(ctx.guild.id, "bloxlink_api_key", key)
        await safe_send(ctx.channel, "✅ Bloxlink key saved.")
    else:
        await safe_send(ctx.channel, "❌ Invalid Bloxlink key.")

@bot.command()
async def set_trello_key(ctx, key: str):
    if validate_trello_key(key):
        set_server_setting(ctx.guild.id, "trello_api_key", key)
        await safe_send(ctx.channel, "✅ Trello API key saved.")
    else:
        await safe_send(ctx.channel, "❌ Invalid Trello API key.")

@bot.command()
async def set_trello_token(ctx, token: str):
    config = load_config(str(ctx.guild.id))

    if "trello_api_key" not in config:
        return await safe_send(ctx.channel, "❌ Set Trello key first.")
    
    print(config["trello_api_key"])

    print(validate_trello_token(config["trello_api_key"], token))
    
    if validate_trello_token(config["trello_api_key"], token):
        set_server_setting(ctx.guild.id, "trello_token", token)
        await safe_send(ctx.channel, "✅ Trello token saved.")
    else:
        await safe_send(ctx.channel, "❌ Invalid Trello token.")

@bot.command()
async def set_trello_board_id(ctx, board_id: str):
    config = load_config(str(ctx.guild.id))
    if "trello_api_key" not in config or "trello_token" not in config:
        return await safe_send(ctx.channel, "❌ Set Trello key and token first.")
    if validate_trello_board(config["trello_api_key"], config["trello_token"], board_id):
        set_server_setting(ctx.guild.id, "trello_board_id", board_id)
        await safe_send(ctx.channel, "✅ Trello board ID saved.")
    else:
        await safe_send(ctx.channel, "❌ Invalid Trello board ID.")

@bot.command()
async def set_trello_list_id(ctx, list_id: str):
    config = load_config(str(ctx.guild.id))
    if "trello_api_key" not in config or "trello_token" not in config:
        return await safe_send(ctx.channel, "❌ Set Trello key and token first.")
    if validate_trello_list(config["trello_api_key"], config["trello_token"], list_id):
        set_server_setting(ctx.guild.id, "trello_list_id", list_id)
        await safe_send(ctx.channel, "✅ Trello list ID saved.")
    else:
        await safe_send(ctx.channel, "❌ Invalid Trello list ID.")

                
#------------------------------------------------------------------------------


@bot.command()
async def setup_status(ctx):
    config = load_config(str(ctx.guild.id))

    def check(key):
        return "✅" if key in config and config[key] else "❌"

    status_text = (
        f"{check('booster_role_id')} Booster role\n"
        f"{check('logs_channel_id')} Logs channel\n"
        f"{check('bloxlink_api_key')} Bloxlink API key\n"
        f"{check('trello_api_key')} Trello API key\n"
        f"{check('trello_token')} Trello token\n"
        f"{check('trello_board_id')} Trello board id\n"
        f"{check('trello_list_id')} Trello booster list id"
    )

    embed = discord.Embed(
        title="🛠️  Setup status",
        color=discord.Color.dark_gray()
    )

    embed.add_field(name="\u200b", value=status_text, inline=False)
    await safe_send(ctx.channel, embed=embed)

        
 #------------------------------------------------------------------------------


@bot.command()
async def commands(ctx):
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

        
 #------------------------------------------------------------------------------


@bot.command()
async def show_json(ctx):
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


 #------------------------------------------------------------------------------


@bot.command()
async def setup(ctx, *, args: str):
    guild = str(ctx.guild)


    # Parse arguments into a dictionary
    pairs = args.split()
    data = {}
    for pair in pairs:
        if "=" not in pair:
            await safe_send(ctx.channel, f"❌ Invalid format: `{pair}` (use key=value)")
            return
        key, value = pair.split("=", 1)
        data[key.strip()] = value.strip()

    # Validate required keys
    required_keys = [
        "booster_role", "logs_channel", "bloxlink_key",
        "trello_key", "trello_token", "trello_board_id", "trello_list_id"
    ]
    missing = [k for k in required_keys if k not in data]
    if missing:
        await safe_send(ctx.channel, f"❌ Missing keys: {', '.join(missing)}")
        return

    # Validate and apply
    try:
        # Roles and channels
        booster_role = guild.get_role(int(data["booster_role"]))
        logs_channel = guild.get_channel(int(data["logs_channel"]))
        if not booster_role or not logs_channel:
            await safe_send(ctx.channel, "❌ Invalid role or channel ID.")
            return

        # Trello API checks
        if not validate_trello_key(data["trello_key"]):
            return await safe_send(ctx.channel, "❌ Invalid Trello key.")
        if not validate_trello_token(data["trello_key"], data["trello_token"]):
            return await safe_send(ctx.channel, "❌ Invalid Trello token.")
        if not validate_trello_board(data["trello_key"], data["trello_token"], data["trello_board_id"]):
            return await safe_send(ctx.channel, "❌ Invalid Trello board ID.")
        if not validate_trello_list(data["trello_key"], data["trello_token"], data["trello_list_id"]):
            return await safe_send(ctx.channel, "❌ Invalid Trello list ID.")

        # Save config
        set_server_setting(guild.id, "booster_role_id", int(data["booster_role"]))
        set_server_setting(guild.id, "logs_channel_id", int(data["logs_channel"]))
        set_server_setting(guild.id, "bloxlink_api_key", data["bloxlink_key"])
        set_server_setting(guild.id, "trello_api_key", data["trello_key"])
        set_server_setting(guild.id, "trello_token", data["trello_token"])
        set_server_setting(guild.id, "trello_board_id", data["trello_board_id"])
        set_server_setting(guild.id, "trello_list_id", data["trello_list_id"])

        await safe_send(ctx.channel, "✅ Setup completed successfully.")
    except Exception as e:
        print("Setup error:", e)
        await safe_send(ctx.channel, "❌ An error occurred during setup.")


@bot.command()
async def set_prefix(ctx):
    global prefix
    prefix = ctx


suggestions_channel_id = 1363260531598819512

#------------------------------------------------ SUGGESTIONS -------------------------------------------------------


# @bot.event
# async def on_message(message):
#     if message.author == bot.user:
#         return

#     if message.channel.id != suggestions_channel_id:
#         return


#     embed = discord.Embed(
#         description=message.content,
#         color=discord.Color.yellow()
#     )

#     embed.set_footer(
#         text=f"{message.author}  •  {message.created_at.strftime('%m/%d/%Y %I:%M %p')}",
#         icon_url=message.author.display_avatar.url
#     )

#     embed.set_author(
#         name="Suggestion「 Under Review 」",
#         icon_url="https://cdn.discordapp.com/attachments/943185637375356998/1363258359368646686/toaster.png?ex=680560c8&is=68040f48&hm=04d37c7d42b6a9f7beceeef394940ab87b0c28df3bb5c2c30f0187ec091ae2cb&"  # example icon
#     )

#     sent = await message.channel.send(embed=embed)

#     await sent.add_reaction("👍")
#     await sent.add_reaction("👎")

#     await message.delete()


#     await bot.process_commands(message)




# @bot.command()
# async def suggestion_status(ctx, message_id: int, status: str, *, note: str = None):
#     try:
#         channel = ctx.channel
#         message = await channel.fetch_message(message_id)

#         if not message.embeds:
#             return await ctx.send("❌ That message has no embed.")

#         embed = message.embeds[0]  # Get the first embed

#         # Base icon changes
#         approved_icon = "https://cdn-icons-png.flaticon.com/512/845/845646.png"
#         disapproved_icon = "https://cdn-icons-png.flaticon.com/512/463/463612.png"

#         if status.lower() == "approved":
#             embed.color = discord.Color.green()
#             icon = approved_icon
#             title = "Approved"
#         elif status.lower() == "disapproved":
#             embed.color = discord.Color.red()
#             icon = disapproved_icon
#             title = "Disapproved"
#         else:
#             return await ctx.send("❌ Status must be `approved` or `disapproved`.")

#         # Build the updated header
#         if note:
#             header = f"{title}「 {note} 」"
#         else:
#             header = f"{title}"

#         embed.set_author(name=header, icon_url=icon)

#         await message.edit(embed=embed)
#         await ctx.send("✅ Suggestion status updated.")

#     except discord.NotFound:
#         await ctx.send("❌ Message not found. Make sure the ID is from this channel.")
#     except discord.Forbidden:
#         await ctx.send("❌ I don't have permission to edit that message.")
#     except discord.HTTPException:
#         await ctx.send("❌ Failed to update the message.")


#     await bot.process_commands(message)


bot.run(BOT_TOKEN)



  

