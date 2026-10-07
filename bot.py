import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"تم تشغيل البوت: {bot.user}")

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="welcome")

    if channel:
        await channel.send(
            f"👋 مرحباً {member.mention} في **{member.guild.name}**!\n"
            f"🎉 نتمنى لك وقتاً ممتعاً!"
        )

token = os.getenv("TOKEN")

if not token:
    raise ValueError("لم يتم وضع TOKEN")

bot.run(token)
