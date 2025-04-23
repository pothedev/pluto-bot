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
import asyncio

from functions.firebase_config import db

from utils.safe_send import safe_send



keep_alive()  # start the fake server 


load_dotenv() 
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")



intents = discord.Intents.default()
intents.message_content = True
intents.members = True  

prefix = "m!"

bot = commands.Bot(command_prefix=prefix, intents=intents)


async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and filename != "__init__.py":
            await bot.load_extension(f"cogs.{filename[:-3]}")


@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")



async def main():
    async with bot:
        await load_cogs()
        await bot.start(BOT_TOKEN) 


asyncio.run(main())



  

