import discord
from discord.ext import commands
from data import SERVER_ID, BOOSTER_ROLE_ID, BOT_TOKEN, LOGS_CHANNEL_ID
from append_user import append_booster
from get_username import get_username
from get_cards import get_cards
from remove_user import remove_booster
from keepalive import keep_alive

keep_alive()  # start the fake server 


intents = discord.Intents.default()
intents.message_content = True
intents.members = True  

prefix = "!"

bot = commands.Bot(command_prefix="!", intents=intents)



def is_duplicate(label):
  labels = get_cards()[1]
  if label in labels:
    return True
  else:
    return False



def append_user(discord_user_id):
  roblox_user = get_username(discord_user_id)
  print(roblox_user)
  append_booster(roblox_user)



@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")


@bot.command()
async def update(ctx, role_arg: str, amount_arg: str):
    logs_channel = ctx.guild.get_channel(int(LOGS_CHANNEL_ID))

    if role_arg.lower() != "booster":
        await ctx.send("Invalid role. Only `booster` is supported.")
        return

    guild = ctx.guild
    if not guild:
        await ctx.send("Server not found.")
        return

    booster_role = discord.utils.get(guild.roles, id=int(BOOSTER_ROLE_ID))
    if not booster_role:
        await ctx.send("Booster role not found.")
        return

    #update all boosters
    if amount_arg.lower() == "all":
        logs_channel.send("Bulk booster update was triggered")
        updated = 0
        skipped = 0
        for member in booster_role.members: 
            discord_id = str(member.id)
            roblox_user = get_username(discord_id)
            if roblox_user:
                if not is_duplicate(roblox_user):
                    append_booster(roblox_user)
                    updated += 1
                    await logs_channel.send(f"✅ User {member} was added to the booster list as {roblox_user}.")
                else:
                    await logs_channel.send(f"⚠️ User {member} is already in the booster list as {roblox_user}. Skipped.")
            else:
                await logs_channel.send(f"❌ Roblox username was not found for {member}.")
                skipped += 1
        message = ""
        if skipped == 1:
            message = f"Didn't find roblox account for {skipped} booster"
        elif skipped > 0:
            message = f"Didn't find roblox account for {skipped} booster"
        await ctx.send(f"✅ Booster list updated for {updated} boosters. {message}")
        await logs_channel.send(f"✅ Booster list updated for {updated} boosters. {message}")
        return

    #update a specific user
    target_member = None
    if ctx.message.mentions:
        target_member = ctx.message.mentions[0]
    else:
        try:
            target_member = await commands.MemberConverter().convert(ctx, amount_arg)
        except:
            await ctx.send("❌ Couldn't find the specified user.")
            return

    if booster_role not in target_member.roles:
        await ctx.send("❌ This user doesn't have the booster role.")
        return

    discord_id = str(target_member.id)
    try:
        roblox_user = get_username(discord_id)
        if roblox_user:
            if not is_duplicate(roblox_user):
                append_booster(roblox_user)
                await ctx.send(f"✅ User {member} was added to the booster list as {roblox_user}.")
                await logs_channel.send(f"✅ User {member} was added to the booster list as {roblox_user}.")
            else:
                await ctx.send(f"⚠️ User {member} is already in the booster list as {roblox_user}.")
        else:
            await ctx.send("❌ Roblox username not found.")
    except Exception as e:
        print(f"Error updating {discord_id}: {e}")
        await ctx.send("❌ Something went wrong while updating.")



@bot.event
async def on_member_update(before, after):
    logs_channel = after.guild.get_channel(int(LOGS_CHANNEL_ID))
    booster_role = discord.utils.get(after.guild.roles, id=int(BOOSTER_ROLE_ID))
    
    if not booster_role:
        print("Booster role not found.")
        return

    had_booster = booster_role in before.roles
    has_booster = booster_role in after.roles

    discord_id = str(after.id)
    roblox_user = get_username(discord_id)

    #auto add
    if not had_booster and has_booster:
        if roblox_user:
            if not is_duplicate(roblox_user):
                append_booster(roblox_user)
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
            remove_booster(roblox_user)
            if logs_channel:
                await logs_channel.send(f"✅ {after.mention} unboosted the server and was removed from Trello as **{roblox_user}**.")
        else:
            if logs_channel:
                await logs_channel.send(f"⚠️ {after.mention} unboosted the server. Roblox username not found.")



bot.run(BOT_TOKEN)



  

