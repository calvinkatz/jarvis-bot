import configparser
import asyncio
import discord
import os
import time
import traceback
from discord.ext import tasks, commands

class JarvisCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        embed = discord.Embed(title="Error")
        if isinstance(error, commands.CommandInvokeError):
            error = error.original
        if isinstance(error, ZeroDivisionError):
            embed.description = "Division by zero attempt"
        if isinstance(error, MissingRequiredArgument):
            embed.description = "You forgot the prompt text idiot"
        else:
            error_data = "".join(traceback.format_exception(type(error), error, error.__traceback__))
            embed.description = f"Unknown error\n```py\n{error_data[:1000]}\n```"
        await ctx.send(embed=embed)

    async def generate_image(self, prompt, usellm):
        # Save positive prompt
        now = int(time.time())
        with open("prompts/{}.txt".format(now), "w") as f:
            f.write(prompt)
        # Run helper script
        if usellm == True:
            cmd = "./helper.sh {} llm".format(now)
        else:
            cmd = "./helper.sh {}".format(now)
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        filename = stdout.decode().rstrip()
        # If no error updload image
        if stderr.decode() != "":
            return ""
        else:
            return filename

    @commands.command()
    async def jarvis(self, ctx, *, arg):
        image = await self.generate_image(arg, False)
        if image != "":
            await ctx.send("Enjoy your creation!", file=discord.File(image))
        else:
            await ctx.send("Image generation failed! :(")

    @commands.command()
    async def prompt(self, ctx, *, arg):
        image = await self.generate_image(arg, True)
        if image != "":
            await ctx.send("Enjoy your creation!", file=discord.File(image))
        else:
            await ctx.send("Image generation failed! :(")

    @commands.command()
    async def count(self, ctx):
        cmd = "ls -1 ./images | wc -l"
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        count = stdout.decode().rstrip()
        if stderr.decode() == "":
            await ctx.send("You have generated {} images!".format(count))
        else:
            await ctx.send("I couldn't count! :(")

    @commands.command(aliases=['ckpt'])
    async def checkpoint(self, ctx):
        config = configparser.ConfigParser()
        config.read('jarvis.conf')
        checkpoint = config['comfyui']['checkpoint']
        await ctx.send("The current checkpoint is: {}".format(checkpoint))

    @commands.command()
    async def poll(self, ctx):
        config = configparser.ConfigParser()
        config.read('jarvis.conf')
        model_dir = config['comfyui']['model_dir']

        print("Starting poll")
        cmd = "ls -1 {}".format(model_dir)
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        checkpoints = stdout.decode().rstrip().split('\n')
        if stderr.decode() == "":
            print("Creating poll")
            from datetime import timedelta
            delta = timedelta(hours=1.0)
            checkpoint_poll = discord.Poll("Which checkpoint would you like?", duration=delta)
            for line in checkpoints:
                print("Adding: {}".format(line))
                checkpoint_poll.add_answer(text=line)
            await ctx.send(poll=checkpoint_poll)
            print("Poll sent")
            print("Sleeping")
            time.sleep(30)
            print("Ending poll")
            await checkpoint_poll.end()
        else:
            await ctx.send("I couldn't find checkpoints! :(")

    @commands.command()
    async def wc(self, ctx):
        cmd = "./wc.sh"
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        if stderr.decode() == "":
            await ctx.send("", file=discord.File("wc.png"))
        else:
            await ctx.send("Word cloud failed! :(")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user and message.type == discord.MessageType.poll_result:
            print("Poll Results")
            embed = message.embeds[0].fields
            result = embed[len(embed)-1]
            print(result.value)
            if result.value != "0":
                config = configparser.ConfigParser()
                config.read('jarvis.conf')
                config['comfyui']['checkpoint'] = result.value
                with open("jarvis.conf", "w") as f:
                    config.write(f)
                print("Checkpoint saved")
                print("Loading model")
                cmd = "./load_model.sh"
                proc = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE)

                stdout, stderr = await proc.communicate()
                print("Model loaded")
            else:
                print("No result, not changing.")

async def setup(bot):
        await bot.add_cog(JarvisCog(bot))
