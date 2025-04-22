import discord
from utils.safe_send import safe_send
from functions.setup_functions import is_bot_setup, load_config
from functions.get_username import get_username
from functions.get_cards import get_cards
from functions.append_user import append_booster
from functions.remove_user import remove_booster

from discord.ext import commands

def is_duplicate(label, guild_id):
  labels = get_cards(guild_id)[1]
  if label in labels:
    return True
  else:
    return False


class AutoMemberUpdate(commands.Cog):
    def __init__(self, bot):
        self.bot=bot

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
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

            if had_booster == has_booster:
                return

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



class ManualMemberUpdate(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def update(self, ctx, role_arg: str, amount_arg: str):
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




async def setup(bot):
    await bot.add_cog(AutoMemberUpdate(bot))
    await bot.add_cog(ManualMemberUpdate(bot))