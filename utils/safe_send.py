import discord

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