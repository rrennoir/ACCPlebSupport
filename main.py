import discord
from discord.ext import commands
import json
import asyncio
import sys
from pprint import pprint
from random import choice, randint


class AccBot(commands.Bot):
    def __init__(self, command_prefix: str, only_link=False, description=None,
                 **options):
        super().__init__(command_prefix, description=description)
        self.admin_pwd: str = "12345"
        self.config: dict = None
        self.token: str = None
        self.leaderboard: dict = None
        self.leaderboard_modified: bool = False
        self.only_link = only_link

        self.bg_task = self.loop.create_task(
            self.save_leaderbard("./leaderboard.json"))

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

        await self.wait_until_ready()
        while not self.is_closed():

            await asyncio.sleep(60)
            if self.leaderboard_modified:
                with open(path, "w") as leaderboard_fp:
                    print("Saving leaderboard...")
                    json.dump(self.leaderboard, leaderboard_fp)
                    self.leaderboard_modified = False
                    print("Leaderboard saved.")

    async def get_leaderboard_time(self, ctx: commands.Context, track: str):

        try:
            driver = ctx.author.name
            i = 0
            i_max = len(self.leaderboard[track])
            while i < i_max and self.leaderboard[track][i]["driver"] != driver:
                i += 1

            if i != i_max:
                time = self.leaderboard[track][i]["time"]
                car = self.leaderboard[track][i]["car"]
                await ctx.send(f"Your best time is a {time} in the {car}")

            else:
                await ctx.send(f"{track} desn't have a time yet,"
                               "may be add yours !")

        except KeyError:
            if track in self.config["tracks"]:
                await ctx.send(f"{track} desn't have a time yet,"
                               "may be add yours !")

            else:
                await ctx.send("Unkown track!")

    async def get_leaderboard_ranking(self, ctx: commands.Context, track: str):
        try:
            entries: dict = self.leaderboard[track].copy()
            ranking = ""
            ordered_entries = []
            while len(ordered_entries) < 10:
                fastest = None
                for driver in entries.key():
                    fastest = driver

        except KeyError:
            if track in self.config["tracks"]:
                await ctx.send(
                    f"{track} desn't have a time yet, may be add yours !")

            else:
                await ctx.send("Unkown track!")

    async def add_leaderboard_time(self, ctx: commands.Context,
                                   track: str, car: str, new_time: str):
        driver = ctx.author.name
        try:
            track_ranking = self.leaderboard[track]

            old_index = 0
            improved = False
            new_index = None
            for entry in track_ranking:
                print(entry)
                if entry["driver"] == driver and entry["car"] == car:
                    old_index = track_ranking.index(entry)
                    improved = entry["time"] > new_time

                if entry["time"] > new_time and not new_index:
                    new_index = track_ranking.index(entry)

            if improved:
                track_ranking.pop(old_index)

                track_ranking.insert(new_index, {
                    "driver": driver,
                    "car": car,
                    "time": new_time
                })

                self.leaderboard_modified = True

            else:
                await ctx.send("You didn't have improved your time"
                               f"at {track} of {new_time}")

        except KeyError:
            if track in self.config["tracks"]:
                self.leaderboard.update({track: [{
                    "driver": driver,
                    "car": car,
                    "time": new_time}]})
                self.leaderboard_modified = True

            else:
                await ctx.send("Unkown track and!")

    async def del_leaderboard_time(self, ctx: commands.Context, track: str,
                                   car: str):

        driver = ctx.author.name
        try:
            entries = self.leaderboard[track]
            i = 0
            i_max = len(entries)
            while (i < i_max and entries[i]["driver"] != driver
                   and entries[i]["car"] != car):
                i += 1

            if i != i_max:
                time = self.leaderboard[track][i]["time"]
                self.leaderboard[track].pop(i)
                self.leaderboard_modified = True

                await ctx.send(f"Removed entry {time} of {driver}"
                               f" with {car} at {track}")

        except KeyError:
            if track in self.config["tracks"]:
                await ctx.send("You didn't have a time in the leaderboard.")

            else:
                await ctx.send("Unkown track!")


only_link = len(sys.argv) > 1 and sys.argv[1] == "-onlylink"
desc = "Hello I'm the techsupport for the ACC plebs !"
bot = AccBot(command_prefix="!", only_link=only_link, description=desc)
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
        if bot.only_link:
            track_map_link = bot.config["track_url"][track_name]
            await ctx.send(track_map_link)
        else:
            track_map = discord.File(f"./TrackMaps/{track_name}.png")
            await ctx.send(file=track_map)

    elif track_name == "?":
        await ctx.send(bot.config["track"])

    else:
        await ctx.send(f"'{track_name}' doesn't exist.\n"
                       "Use `track ?` for the track list.")


@bot.command()
async def pressures(ctx: commands.Context, condition: str = None):

    condition = condition.lower()
    if condition == "dry":
        await ctx.send("Optimal hot pressure is betwen 27.5 and 28 Psi.")

    elif condition == "wet":
        await ctx.send("Optimal hot pressure is betwen 29.5 and 30 Psi.")

    else:
        await ctx.send(
            "Around 27.5 to 28 Psi on the dry\n29.5 to 30 on the Wet.")


@bot.command()
async def leaderboard(ctx: commands.Context, *args):

    help_txt = ("How to use: `!leaderboard 'track'"
                "[add/del/ranking] [time to add]`")
    if len(args) == 1:

        track = args[0].lower()
        await bot.get_leaderboard_time(ctx, track)

    elif len(args) == 2:

        option = args[1].lower()
        track = args[0].lower()

        if option == "ranking":
            await bot.get_leaderboard_ranking(ctx, track)

        else:
            await ctx.send(help_txt)

    elif len(args) == 3:

        if args[1] == "del":
            track = args[0].lower()
            car = args[2].lower()

            await bot.del_leaderboard_time(ctx, track, car)

    elif len(args) == 4:

        if args[1].lower() == "add":
            track = args[0].lower()
            car = args[2].lower()
            time = args[3]
            # TODO find a better way for time check
            if len(time) == 8:
                if car in bot.config["cars"]:
                    await bot.add_leaderboard_time(ctx, track, car, time)
                else:
                    await ctx.send("Incorrect car name\n"
                                   "Use `!cars` for the list.")

            else:
                await ctx.send("Incorrecte time format!\n"
                               "It should be `0:00.000`")

        else:
            await ctx.send(help_txt)

    else:
        await ctx.send(help_txt)


@bot.command()
async def stop(ctx, pwd: str = None):

    if pwd == bot.admin_pwd:
        print("Shuting down.\nBye!")
        await ctx.send("Shuting down...")
        await bot.close()

    else:
        await ctx.send("Invalide password.")


print("Starting bot...")
bot.run(bot.token)
