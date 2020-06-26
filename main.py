import discord
from random import choice, randint
# from discord.ext import commands


class Botclient(discord.Client):

    cars = [
        "ferrari 488",
        "Aston Martin V8"
        "Audi R8 evo",
        "Porsche 911.2 GT3 R"
    ]

    track_list = [
        "spa",
        "monza",
        "brands_hatch",
        "barcelona"
    ]

    emoji_list = [
        "kappa",
        "THINKING_HD"
    ]

    async def on_ready(self):

        print(f"Logged on as {self.user}")

    async def on_message(self, message):

        if message.author != self.user:

            if message.content[0] == "!":

                command = message.content.lower().split()
                print(f"Receved command: {command}")

                if command[0] == "!map":
                    await self.track_maps(command[1], message.channel)

                if command[0] == "!randomcar":
                    await message.channel.send(choice(Botclient.cars))

            elif message.content.split(":")[1] in Botclient.emoji_list and randint(0, 100) <= 10:
                guild = discord.utils.get(client.guilds, name='Alpiniste Aveugle')

                emoji = discord.utils.get(guild.emojis, name=message.content.split(":")[1])
                await message.channel.send(emoji)

    async def track_maps(self, track, channel):

        if track in Botclient.track_list:
            trackmap = discord.File(f"./TrackMaps/{track}.png")
            await channel.send(f"Theres is the map of {track}", file=trackmap)

        else:
            await channel.send(f"'{track}' doesn't exist.")


with open("./Token.txt") as token_file:
    token = token_file.readline()

client = Botclient()
client.run(token)
