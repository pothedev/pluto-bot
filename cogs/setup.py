import discord
from discord.ext import commands

from utils.safe_send import safe_send
from utils.is_authorized_user import is_authorized_user
from functions.setup_functions import set_server_setting, validate_trello_key, validate_trello_token, load_config, validate_trello_board, validate_trello_list



# -------------------- Discord ------------------------

class SetBoosterRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command()
    # @is_authorized_user()
    async def set_booster_role(self, ctx, role: discord.Role):
        if not is_authorized_user(ctx):
            safe_send(ctx, "you aint authorized")
            return
        else: print("ok user authorized, changing booster role")
        if role in ctx.guild.roles:
            set_server_setting(ctx.guild.id, "booster_role_id", role.id)
            await safe_send(ctx.channel, f"✅ Booster role set to {role.name}.")
        else:
            await safe_send(ctx.channel, "❌ Role not found in this server.")


class SetGiveawayManagerRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def set_giveaway_manager_role(self, ctx, role: str):
        if not is_authorized_user(ctx):
            await safe_send(ctx, "you aint authorized")
            return
        else: print("ok user authorized, changing giveaway manager role")

        try:
            if role.startswith("<@&") and role.endswith(">"):
                role_id = int(role[3:-1])
            else:
                role_id = int(role)

            resolved_role = ctx.guild.get_role(role_id)
        except ValueError:
            resolved_role = discord.utils.find(lambda r: r.name == role, ctx.guild.roles)

        if resolved_role is None:
            await safe_send(ctx.channel, "❌ Role not found.")
            return

        set_server_setting(ctx.guild.id, "giveaway_manager_role_id", resolved_role.id)
        await safe_send(ctx.channel, f"✅ Giveaway manager role set to {resolved_role.name}")



class SetGameshowHostRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def set_gameshow_host_role(self, ctx, role: str):
        if not is_authorized_user(ctx):
            await safe_send(ctx, "you aint authorized")
            return
        else: print("ok user authorized, changing gameshow host role")

        try:
            if role.startswith("<@&") and role.endswith(">"):
                role_id = int(role[3:-1])
            else:
                role_id = int(role)

            resolved_role = ctx.guild.get_role(role_id)
        except ValueError:
            resolved_role = discord.utils.find(lambda r: r.name == role, ctx.guild.roles)

        if resolved_role is None:
            await safe_send(ctx.channel, "❌ Role not found.")
            return

        set_server_setting(ctx.guild.id, "gameshow_host_role_id", resolved_role.id)
        await safe_send(ctx.channel, f"✅ Gameshow host role set to {resolved_role.name}")


class SetGiveawayPingRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def set_giveaway_ping_role(self, ctx, role: str):
        if not is_authorized_user(ctx):
            await safe_send(ctx, "you aint authorized")
            return
        else: print("ok user authorized, changing giveaway ping role")

        try:
            if role.startswith("<@&") and role.endswith(">"):
                role_id = int(role[3:-1])
            else:
                role_id = int(role)

            resolved_role = ctx.guild.get_role(role_id)
        except ValueError:
            resolved_role = discord.utils.find(lambda r: r.name == role, ctx.guild.roles)

        if resolved_role is None:
            await safe_send(ctx.channel, "❌ Role not found.")
            return

        set_server_setting(ctx.guild.id, "giveaway_ping_role_id", resolved_role.id)
        await safe_send(ctx.channel, f"✅ Giveaway ping role set to {resolved_role.name}")



class SetGameshowPingRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def set_gameshow_ping_role(self, ctx, role: str):
        if not is_authorized_user(ctx):
            await safe_send(ctx, "you aint authorized")
            return
        else: print("ok user authorized, changing gameshow ping role")

        try:
            if role.startswith("<@&") and role.endswith(">"):
                role_id = int(role[3:-1])
            else:
                role_id = int(role)

            resolved_role = ctx.guild.get_role(role_id)
        except ValueError:
            resolved_role = discord.utils.find(lambda r: r.name == role, ctx.guild.roles)

        if resolved_role is None:
            await safe_send(ctx.channel, "❌ Role not found.")
            return

        set_server_setting(ctx.guild.id, "gameshow_ping_role_id", resolved_role.id)
        await safe_send(ctx.channel, f"✅ Gameshow ping role set to {resolved_role.name}")




class SetLogsChannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command()
    # @is_authorized_user()
    async def set_logs_channel(self, ctx, channel: discord.TextChannel):
      if not is_authorized_user(ctx):
        safe_send(ctx, "you aint authorized")
        return
      else: print("ok user authorized, changing logs channel")
      if channel in ctx.guild.text_channels:
          set_server_setting(ctx.guild.id, "logs_channel_id", channel.id)
          await safe_send(ctx.channel, f"✅ Logs channel set to {channel.mention}.")
      else:
          await safe_send(ctx.channel, "❌ Channel not found in this server.")


class SetGiveawayChannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command()
    async def set_giveaway_channel(self, ctx, channel: discord.TextChannel):
      if not is_authorized_user(ctx):
        safe_send(ctx, "you aint authorized")
        return
      else: print("ok user authorized, changing giveaway channel")
      if channel in ctx.guild.text_channels:
          set_server_setting(ctx.guild.id, "giveaway_channel_id", channel.id)
          await safe_send(ctx.channel, f"✅ Giveaway channel set to {channel.mention}.")
      else:
          await safe_send(ctx.channel, "❌ Channel not found in this server.")

class SetGameshowChannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command()
    async def set_gameshow_channel(self, ctx, channel: discord.TextChannel):
      if not is_authorized_user(ctx):
        safe_send(ctx, "you aint authorized")
        return
      else: print("ok user authorized, changing gameshow channel")
      if channel in ctx.guild.text_channels:
          set_server_setting(ctx.guild.id, "gameshow_channel_id", channel.id)
          await safe_send(ctx.channel, f"✅ Gameshow channel set to {channel.mention}.")
      else:
          await safe_send(ctx.channel, "❌ Channel not found in this server.")

class SetPingCdChannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command()
    #@is_authorized_user()
    async def set_ping_cd_channel(self, ctx, channel: discord.TextChannel):
      if not is_authorized_user(ctx):
        safe_send(ctx, "you aint authorized")
        return
      else: print("ok user authorized, changing ping cd channel")
      if channel in ctx.guild.text_channels:
          set_server_setting(ctx.guild.id, "ping_cd_channel_id", channel.id)
          await safe_send(ctx.channel, f"✅ Ping cd channel set to {channel.mention}.")
      else:
          await safe_send(ctx.channel, "❌ Channel not found in this server.")  


class SetStaffRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def set_staff_role(self, ctx, role: str):
        if not is_authorized_user(ctx):
            await safe_send(ctx, "you aint authorized")
            return
        else: print("ok user authorized, changing staff role")

        try:
            if role.startswith("<@&") and role.endswith(">"):
                role_id = int(role[3:-1])
            else:
                role_id = int(role)

            resolved_role = ctx.guild.get_role(role_id)
        except ValueError:
            resolved_role = discord.utils.find(lambda r: r.name == role, ctx.guild.roles)

        if resolved_role is None:
            await safe_send(ctx.channel, "❌ Role not found.")
            return

        set_server_setting(ctx.guild.id, "staff_role_id", resolved_role.id)
        await safe_send(ctx.channel, f"✅ Staff role set to {resolved_role.id}")



# -------------------- Bloxlink ------------------------

class SetBloxlinkKey(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command()
    # @is_authorized_user()
    async def set_bloxlink_key(self, ctx, key: str):
        if not is_authorized_user(ctx):
            safe_send(ctx, "you aint authorized")
            return
        else: print("ok user authorized, changing bloxlink key")
        if len(key) > 10:
            set_server_setting(ctx.guild.id, "bloxlink_api_key", key)
            await safe_send(ctx.channel, "✅ Bloxlink key saved.")
        else:
            await safe_send(ctx.channel, "❌ Invalid Bloxlink key.")



# -------------------- Trello ------------------------

class SetTrelloKey(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command()
    # @is_authorized_user()
    async def set_trello_key(self, ctx, key: str):
      if not is_authorized_user(ctx):
        safe_send(ctx, "you aint authorized")
        return
      else: print("ok user authorized, changing trello key")
      if validate_trello_key(key):
          set_server_setting(ctx.guild.id, "trello_api_key", key)
          await safe_send(ctx.channel, "✅ Trello API key saved.")
      else:
          await safe_send(ctx.channel, "❌ Invalid Trello API key.")


class SetTrelloToken(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command()
    # @is_authorized_user()
    async def set_trello_token(self, ctx, token: str):
        if not is_authorized_user(ctx):
            safe_send(ctx, "you aint authorized")
            return
        else: print("ok user authorized, changing trello token")
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


class SetTrelloBoardId(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command()
    # @is_authorized_user()
    async def set_trello_board_id(self, ctx, board_id: str):
        if not is_authorized_user(ctx):
            safe_send(ctx, "you aint authorized")
            return
        else: print("ok user authorized, changing trello board id")
        config = load_config(str(ctx.guild.id))
        if "trello_api_key" not in config or "trello_token" not in config:
            return await safe_send(ctx.channel, "❌ Set Trello key and token first.")
        if validate_trello_board(config["trello_api_key"], config["trello_token"], board_id):
            set_server_setting(ctx.guild.id, "trello_board_id", board_id)
            await safe_send(ctx.channel, "✅ Trello board ID saved.")
        else:
            await safe_send(ctx.channel, "❌ Invalid Trello board ID.")


class SetTrelloListId(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command()
    # @is_authorized_user()
    async def set_trello_list_id(self, ctx, list_id: str):
        if not is_authorized_user(ctx):
            safe_send(ctx, "you aint authorized")
            return
        else: print("ok user authorized, changing trello list id")
        config = load_config(str(ctx.guild.id))
        if "trello_api_key" not in config or "trello_token" not in config:
            return await safe_send(ctx.channel, "❌ Set Trello key and token first.")
        if validate_trello_list(config["trello_api_key"], config["trello_token"], list_id):
            set_server_setting(ctx.guild.id, "trello_list_id", list_id)
            await safe_send(ctx.channel, "✅ Trello list ID saved.")
        else:
            await safe_send(ctx.channel, "❌ Invalid Trello list ID.")



# -------------------- Suggestions ------------------------

class SetSuggestionsChannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command()
    # @is_authorized_user()
    async def set_suggestions_channel(self, ctx, channel: discord.TextChannel):
        if not is_authorized_user(ctx):
            safe_send(ctx, "you aint authorized")
            return
        else: print("ok user authorized, changing suggestions channel")
        if channel in ctx.guild.text_channels:
            set_server_setting(ctx.guild.id, "suggestions_channel_id", channel.id)
            await safe_send(ctx.channel, f"✅ Suggestions channel set to {channel.mention}.")
        else:
            await safe_send(ctx.channel, "❌ Channel not found in this server.")

  

# -------------------- Whole set up ------------------------


class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    # @is_authorized_user()
    async def setup(self, ctx, *, args: str):
        if not is_authorized_user(ctx):
            safe_send(ctx, "you aint authorized")
            return
        else: print("ok user authorized, changing setup")
        guild = ctx.guild

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
            booster_role = guild.get_role(int(data["booster_role"]))
            logs_channel = guild.get_channel(int(data["logs_channel"]))
            if not booster_role or not logs_channel:
                await safe_send(ctx.channel, "❌ Invalid role or channel ID.")
                return

            if not validate_trello_key(data["trello_key"]):
                return await safe_send(ctx.channel, "❌ Invalid Trello key.")
            if not validate_trello_token(data["trello_key"], data["trello_token"]):
                return await safe_send(ctx.channel, "❌ Invalid Trello token.")
            if not validate_trello_board(data["trello_key"], data["trello_token"], data["trello_board_id"]):
                return await safe_send(ctx.channel, "❌ Invalid Trello board ID.")
            if not validate_trello_list(data["trello_key"], data["trello_token"], data["trello_list_id"]):
                return await safe_send(ctx.channel, "❌ Invalid Trello list ID.")

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


async def setup(bot):
    await bot.add_cog(SetGiveawayManagerRole(bot))
    await bot.add_cog(SetGameshowHostRole(bot))
    await bot.add_cog(SetGiveawayPingRole(bot))
    await bot.add_cog(SetGameshowPingRole(bot))
    await bot.add_cog(SetStaffRole(bot))
    await bot.add_cog(SetBoosterRole(bot))

    await bot.add_cog(SetLogsChannel(bot))
    await bot.add_cog(SetPingCdChannel(bot))
    await bot.add_cog(SetSuggestionsChannel(bot))
    await bot.add_cog(SetGiveawayChannel(bot))
    await bot.add_cog(SetGameshowChannel(bot))

    await bot.add_cog(SetBloxlinkKey(bot))
    await bot.add_cog(SetTrelloKey(bot))
    await bot.add_cog(SetTrelloToken(bot))
    await bot.add_cog(SetTrelloBoardId(bot))
    await bot.add_cog(SetTrelloListId(bot))
    
    await bot.add_cog(Setup(bot))
    
