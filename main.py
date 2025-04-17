import discord
from discord.ext import commands

from append_user import append_booster
from get_username import get_username
from get_cards import get_cards
from remove_user import remove_booster
from setup_functions import *

from keepalive import keep_alive
from dotenv import load_dotenv
import os


load_dotenv() 

BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")


keep_alive()  # start the fake server 


intents = discord.Intents.default()
intents.message_content = True
intents.members = True  

prefix = "m!"

bot = commands.Bot(command_prefix="m!", intents=intents)

CONFIG_FILE = "./config.json"



async def safe_send(channel, content):
    try:
        await channel.send(content)
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
        
        await safe_send(ctx, "❌ Bot is not fully set up. Use `m!setup_status` to check what’s missing.")
        return
    
    config = load_config()
    guild_id = str(ctx.guild.id)
    server_config = config.get(guild_id, {})
    
    logs_channel_id = server_config["logs_channel_id"]
    booster_role_id = server_config["booster_role_id"]
    logs_channel = ctx.guild.get_channel(int(logs_channel_id))

    if role_arg.lower() != "booster":
        await safe_send(ctx, "Invalid role. Only `booster` is supported.")
        return

    guild = ctx.guild
    if not guild:
        safe_send(ctx, "Server not found.")
        return

    booster_role = discord.utils.get(guild.roles, id=int(booster_role_id))
    if not booster_role:
        safe_send(ctx, "Booster role not found.")
        return

    #update all boosters
    if amount_arg.lower() == "all":
        safe_send(logs_channel, "Bulk booster update was triggered")
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
        await safe_send(ctx, f"✅ Booster list updated for {updated} boosters. {message}")
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
            await safe_send(ctx, "❌ Couldn't find the specified user.")
            return

    if booster_role not in target_member.roles:
        await safe_send(ctx, "❌ This user doesn't have the booster role.")
        return

    discord_id = str(target_member.id)
    try:
        roblox_user = get_username(discord_id, str(ctx.guild.id))
        if roblox_user:
            if not is_duplicate(roblox_user, str(ctx.guild.id)):
                append_booster(roblox_user, str(ctx.guild.id))
                await safe_send(ctx, f"✅ User {target_member} was added to the booster list as {roblox_user}.")
                await safe_send(logs_channel, f"✅ User {target_member} was added to the booster list as {roblox_user}.")
            else:
                await safe_send(ctx, f"⚠️ User {target_member} is already in the booster list as {roblox_user}.")
        else:
            await safe_send(ctx,"❌ Roblox username not found.")
    except Exception as e:
        print(f"Error updating {discord_id}: {e}")
        await safe_send(ctx, "❌ Something went wrong while updating.")



#--------------------- auto commands ------------------------

@bot.event
async def on_member_update(before, after):
    if is_bot_setup(after.guild.id):
        config = load_config()
        guild_id = str(after.guild.id)
        server_config = config.get(guild_id, {})

        booster_role_id = server_config["booster_role_id"]
        logs_channel_id = server_config["logs_channel_id"]
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
                        await logs_channel.send(f"✅ {after.mention} boosted the server and was added to Trello as **{roblox_user}**.")
                else:
                    if logs_channel:
                        await logs_channel.send(f"⚠️ {after.mention} boosted the server but is already in the Trello list as **{roblox_user}**.")
            else:
                if logs_channel:
                    await logs_channel.send(f"⚠️ {after.mention} boosted the server. Roblox username not found.")

        #auto remove
        elif had_booster and not has_booster:
            if roblox_user:
                remove_booster(roblox_user, str(after.guild.id))
                if logs_channel:
                    await logs_channel.send(f"✅ {after.mention} unboosted the server and was removed from Trello as **{roblox_user}**.")
            else:
                if logs_channel:
                    await logs_channel.send(f"⚠️ {after.mention} unboosted the server. Roblox username not found.")



# ------------------ set up commands ------------------


@bot.command()
async def init_config(ctx):
    ensure_server_config(ctx.guild.id)
    await ctx.send("✅ Config initialized for this server.")

@bot.command()
async def set_booster_role(ctx, role: discord.Role):
    ensure_server_config(ctx.guild.id)
    if role in ctx.guild.roles:
        set_server_setting(ctx.guild.id, "booster_role_id", role.id)
        await ctx.send(f"✅ Booster role set to {role.name}.")
    else:
        await ctx.send("❌ Role not found in this server.")

@bot.command()
async def set_logs_channel(ctx, channel: discord.TextChannel):
    ensure_server_config(ctx.guild.id)
    if channel in ctx.guild.text_channels:
        set_server_setting(ctx.guild.id, "logs_channel_id", channel.id)
        await ctx.send(f"✅ Logs channel set to {channel.mention}.")
    else:
        await ctx.send("❌ Channel not found in this server.")

@bot.command()
async def set_bloxlink_key(ctx, key: str):
    ensure_server_config(ctx.guild.id)
    if len(key) > 10:
        set_server_setting(ctx.guild.id, "bloxlink_api_key", key)
        await ctx.send("✅ Bloxlink key saved.")
    else:
        await ctx.send("❌ Invalid Bloxlink key.")

@bot.command()
async def set_trello_key(ctx, key: str):
    ensure_server_config(ctx.guild.id)
    if validate_trello_key(key):
        set_server_setting(ctx.guild.id, "trello_api_key", key)
        await ctx.send("✅ Trello API key saved.")
    else:
        await ctx.send("❌ Invalid Trello API key.")

@bot.command()
async def set_trello_token(ctx, token: str):
    ensure_server_config(ctx.guild.id)
    config = load_config()[str(ctx.guild.id)]

    if "trello_api_key" not in config:
        return await ctx.send("❌ Set Trello key first.")
    
    print(config["trello_api_key"])

    print(validate_trello_token(config["trello_api_key"], token))
    
    if validate_trello_token(config["trello_api_key"], token):
        set_server_setting(ctx.guild.id, "trello_token", token)
        await ctx.send("✅ Trello token saved.")
    else:
        await ctx.send("❌ Invalid Trello token.")

@bot.command()
async def set_trello_board_id(ctx, board_id: str):
    ensure_server_config(ctx.guild.id)
    config = load_config()[str(ctx.guild.id)]
    if "trello_api_key" not in config or "trello_token" not in config:
        return await ctx.send("❌ Set Trello key and token first.")
    if validate_trello_board(config["trello_api_key"], config["trello_token"], board_id):
        set_server_setting(ctx.guild.id, "trello_board_id", board_id)
        await ctx.send("✅ Trello board ID saved.")
    else:
        await ctx.send("❌ Invalid Trello board ID.")

@bot.command()
async def set_trello_list_id(ctx, list_id: str):
    ensure_server_config(ctx.guild.id)
    config = load_config()[str(ctx.guild.id)]
    if "trello_api_key" not in config or "trello_token" not in config:
        return await ctx.send("❌ Set Trello key and token first.")
    if validate_trello_list(config["trello_api_key"], config["trello_token"], list_id):
        set_server_setting(ctx.guild.id, "trello_list_id", list_id)
        await ctx.send("✅ Trello list ID saved.")
    else:
        await ctx.send("❌ Invalid Trello list ID.")

                
 #------------------------------------------------------------------------------


@bot.command()
async def setup_status(ctx):
    config = load_config()
    guild_id = str(ctx.guild.id)
    server_config = config.get(guild_id, {})

    def check(key):
        return "✅" if key in server_config and server_config[key] else "❌"

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
    await ctx.send(embed=embed)

        
 #------------------------------------------------------------------------------


@bot.command()
async def helpp(ctx):
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
    await ctx.send(embed=embed)

        
 #------------------------------------------------------------------------------


@bot.command()
async def show_json(ctx):
    try:
        with open("config.json", "r") as f:
            config_data = json.load(f)

        pretty_json = json.dumps(config_data, indent=2)
        if len(pretty_json) > 1900:
            await ctx.send("⚠️ Config is too long to display here.")
        else:
            await ctx.send(f"```json\n{pretty_json}\n```")
    except Exception as e:
        await ctx.send(f"❌ Failed to load config: {e}")


 #------------------------------------------------------------------------------


@bot.command()
async def setup(ctx, *, args: str):
    ensure_server_config(ctx.guild.id)
    guild = ctx.guild
    guild_id = str(guild.id)

    config = load_config().get(guild_id, {})

    # Parse arguments into a dictionary
    pairs = args.split()
    data = {}
    for pair in pairs:
        if "=" not in pair:
            await ctx.send(f"❌ Invalid format: `{pair}` (use key=value)")
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
        await ctx.send(f"❌ Missing keys: {', '.join(missing)}")
        return

    # Validate and apply
    try:
        # Roles and channels
        booster_role = guild.get_role(int(data["booster_role"]))
        logs_channel = guild.get_channel(int(data["logs_channel"]))
        if not booster_role or not logs_channel:
            await ctx.send("❌ Invalid role or channel ID.")
            return

        # Trello API checks
        if not validate_trello_key(data["trello_key"]):
            return await ctx.send("❌ Invalid Trello key.")
        if not validate_trello_token(data["trello_key"], data["trello_token"]):
            return await ctx.send("❌ Invalid Trello token.")
        if not validate_trello_board(data["trello_key"], data["trello_token"], data["trello_board_id"]):
            return await ctx.send("❌ Invalid Trello board ID.")
        if not validate_trello_list(data["trello_key"], data["trello_token"], data["trello_list_id"]):
            return await ctx.send("❌ Invalid Trello list ID.")

        # Save config
        set_server_setting(guild.id, "booster_role_id", int(data["booster_role"]))
        set_server_setting(guild.id, "logs_channel_id", int(data["logs_channel"]))
        set_server_setting(guild.id, "bloxlink_api_key", data["bloxlink_key"])
        set_server_setting(guild.id, "trello_api_key", data["trello_key"])
        set_server_setting(guild.id, "trello_token", data["trello_token"])
        set_server_setting(guild.id, "trello_board_id", data["trello_board_id"])
        set_server_setting(guild.id, "trello_list_id", data["trello_list_id"])

        await ctx.send("✅ Setup completed successfully.")
    except Exception as e:
        print("Setup error:", e)
        await ctx.send("❌ An error occurred during setup.")





bot.run(BOT_TOKEN)



  

