import configparser
import discord
import asyncio
import os
from discord.ext import commands

config = configparser.ConfigParser()
config.read('jarvis.conf')
token = config['bot']['token']

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents, case_insensitive=True)

@bot.command(name="reload")
@commands.is_owner()
async def _reload(ctx):
    await bot.reload_extension("cogs.jarvis")
    embed = discord.Embed(title='Reload', description=f'Jarvis successfully reloaded', color=0xff00c8)
    await ctx.send(embed=embed)

@bot.command(name="commands")
async def _commands(ctx):
    text = '```\n!jarvis `positive` `negative`\nNegative prompt is optional.```'
    await ctx.send(text)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            # cut off the .py from the file name
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(token)

asyncio.run(main())
