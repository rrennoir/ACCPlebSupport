import discord
from discord.ext import commands
import json
from pprint import pprint
from random import choice, randint


class AccBot(commands.Bot):
    def __init__(self, command_prefix, description=None, **options):
        super().__init__(command_prefix, description=description)
        self.admin_pwd = "12345"
        self.config = None
        self.token = None
        self.leaderboard = None

    def load_config(self, path: str):

        print("Loading config...")
        with open(path, "r") as config_file:
            self.config = json.load(config_file)
            pprint(self.config)

    def load_token(self, path: str):

        print("Loading token...")
        with open(path) as token_file:
            self.token = token_file.readline()

    def load_leaderboard(self, path: str):
        try:
            with open(path, "r") as leaderboard_fp:
                self.leaderboard = json.load(leaderboard_fp)

        except FileNotFoundError:
            self.leaderboard = {}

    async def save_leaderbard(self, path: str):
        with open(path, "w") as leaderboard_fp:
            json.dump(self.leaderboard, leaderboard_fp)

    async def get_leaderboard_time(self, ctx: commands.Context, track: str):

        try:
            driver = ctx.author.name
            entry = self.leaderboard[track]
            await ctx.send(entry)

        except KeyError:
            if track in self.config["tracks"]:
                await ctx.send(f"{track} desn't have a time yet, may be add yours !")

            else:
                await ctx.send("Unkown track!")

    async def add_leaderboard_time(self, ctx: commands.Context,
                                   track: str, new_time: str):
        driver = ctx.author.name
        try:
            time = self.leaderboard[track][driver]
            if time > new_time:
                self.leaderboard[track][driver] = new_time

            else:
                await ctx.send(f"You didn't have improved your time at {track} of {time}")

        except KeyError:
            if track in self.config["tracks"]:
                self.leaderboard.update({track: {driver: new_time}})

            else:
                await ctx.send("Unkown track!")


desc = "Hello I'm the techsupport for the ACC plebs !"
bot = AccBot(command_prefix="!", description=desc)
bot.load_config("./config.json")
bot.load_token("./Token.txt")
bot.load_leaderboard("./leaderboard.json")


@bot.event
async def on_ready():
    print("Bot is ready")


@bot.command()
async def save(ctx: commands.Context):
    await bot.save_leaderbard("./leaderboard.json")


@bot.command()
async def randomcar(ctx: commands.Context):
    await ctx.send(choice(bot.config["cars"]))


@bot.command()
async def track(ctx: commands.Context, track_name: str = None):

    if track_name in bot.config["tracks"]:
        track_map = discord.File(f"./TrackMaps/{track_name}.png")
        await ctx.send(file=track_map)

    else:
        await ctx.send(f"'{track_name}' doesn't exist.")


@bot.command()
async def pressures(ctx: commands.Context):
    await ctx.send("Around 27.5 Psi on the dry\n30 on the Wet.")


@bot.command(description="Get the leaderboard of the track or add a your time.")
async def leaderboard(ctx: commands.Context, *args):

    if len(args) == 1:

        track = args[0].lower()
        await bot.get_leaderboard_time(ctx, track)

    elif len(args) == 2:

        track = args[0].lower()
        time = args[1]
        # TODO find a better way for time check
        minute, s_ms = time.split(":")
        second, millisecond = s_ms.split(".")
        if len(minute) == 1 and len(second) == 2 and len(millisecond) == 3:
            await bot.add_leaderboard_time(ctx, track, time)

        else:
            ctx.send("Incorecte time format!\nIt should be `0:00.000`")

    else:
        await ctx.send("How to use: `!leaderboard 'track' [time to add]`")


@bot.command()
async def stop(ctx, pwd):

    if pwd == bot.admin_pwd:
        print("Shuting down.\nBye!")
        await ctx.send("Shuting down...")
        await bot.close()

    else:
        await ctx.send("Invalide password.")


print("Starting bot...")
bot.run(bot.token)
