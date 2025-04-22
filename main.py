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

from utils.safe_send import safe_send
# from cogs.member_update import AutoMemberUpdate, ManualMemberUpdate


async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and filename != "__init__.py":
            await bot.load_extension(f"cogs.{filename[:-3]}")


load_dotenv() 

BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")


keep_alive()  # start the fake server 



intents = discord.Intents.default()
intents.message_content = True
intents.members = True  

prefix = "m!"

bot = commands.Bot(command_prefix=prefix, intents=intents)

CONFIG_FILE = "./config.json"





def is_duplicate(label, guild_id):
  labels = get_cards(guild_id)[1]
  if label in labels:
    return True
  else:
    return False




@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")




@bot.command()
async def set_suggestions_channel(ctx, channel: discord.TextChannel):
    if channel in ctx.guild.text_channels:
        set_server_setting(ctx.guild.id, "suggestions_channel_id", channel.id)
        await safe_send(ctx.channel, f"✅ Suggestions channel set to {channel.mention}.")
    else:
        await safe_send(ctx.channel, "❌ Channel not found in this server.")


                
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



#------------------------------------------------ SUGGESTIONS -------------------------------------------------------


@bot.event
async def on_message(message):

    if not message.guild:
        return

    config = load_config(message.guild.id)
    suggestions_channel_id = config.get("suggestions_channel_id")

    if message.author == bot.user:
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
            icon_url="https://cdn.discordapp.com/attachments/943185637375356998/1363258359368646686/toaster.png"
        )

        sent = await message.channel.send(embed=embed)
        # await sent.add_reaction("👍")
        # await sent.add_reaction("👎")

        await sent.add_reaction("<:mw_thumbsup:893807577148821545>")
        await sent.add_reaction("<:mw_thumbsside:994961972066009138>")
        await sent.add_reaction("<:mw_thumbsdown:893807653933969429>")

        await message.delete()

    # 👇 Must be outside the suggestion channel check
    await bot.process_commands(message)




@bot.command()
async def suggestion_status(ctx, message_id: int, status: str, *, note: str = None):

    config = load_config(ctx.guild.id)

    suggestions_channel_id = config.get("suggestions_channel_id")
    if not suggestions_channel_id:
        return

    
    try:
        channel = bot.get_channel(suggestions_channel_id)
        message = await channel.fetch_message(message_id)

        if not message.embeds:
            return await ctx.send("❌ That message has no embed.")

        embed = message.embeds[0]  # Get the first embed

        # Base icon changes
        approved_icon = "https://cdn.discordapp.com/attachments/943185637375356998/1363261116611956846/FuSIgc6XgAg8_1p.png?ex=6805635a&is=680411da&hm=2018e07f18718e7f5add6e2fbe1323c88ffb163b3528db757e27751ff9bdf663&"
        disapproved_icon = "https://cdn.discordapp.com/attachments/943185637375356998/1363261805996150885/brimstone.png?ex=680563fe&is=6804127e&hm=113ab85c1f34d0f9e4793b0e9bd573250b18129c01b28c506f12a24b86bc5fa2&"

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



async def main():
    async with bot:
        await load_cogs()
        await bot.start(BOT_TOKEN) 

import asyncio
asyncio.run(main())



  

