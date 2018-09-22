import discord
import collections
import datetime
import os

ranks = collections.defaultdict(dict)
start_time = collections.defaultdict(dict)

client = discord.Client()


@client.event
async def on_ready():
    await client.change_presence(game=discord.Game(name="Stalking {} users//nlb.help".
                                                   format(len(tuple(client.get_all_members())))))
    # if online or in-game from beginning
    for member in client.get_all_members():
        if not member.bot:
            if str(member.status) != "offline":
                start_time[member.id]["Online"] = datetime.datetime.now()
            if member.game:
                start_time[member.id][str(member.game)] = datetime.datetime.now()


@client.event
async def on_member_update(before, after):
    if not after.bot:
        # if status changed
        if before.status != after.status:
            # if online
            if str(before.status) == "offline":
                start_time[after.id]["Online"] = datetime.datetime.now()
            # if offline from online
            elif str(after.status) == "offline":
                try:
                    end_time = datetime.datetime.now()
                    total_time = end_time - start_time[after.id].get("Online", 0)
                    ranks[after.id]["Online"] = ranks[after.id].get("Online", 0) + int(total_time.total_seconds())
                    start_time[after.id]["Online"] = 0
                except TypeError:
                    pass
        # if game changed
        if before.game != after.game:
            # if game changes
            if before.game and after.game:
                try:
                    end_time = datetime.datetime.now()
                    total_time = end_time - start_time[after.id].get(str(before.game), 0)
                    ranks[after.id][str(before.game)] = (ranks[after.id].get(str(before.game), 0)
                                                         + int(total_time.total_seconds()))
                    start_time[after.id][str(before.game)] = 0
                except TypeError:
                    pass
                finally:
                    start_time[after.id][str(after.game)] = datetime.datetime.now()
            # if game starts
            elif after.game:
                start_time[after.id][str(after.game)] = datetime.datetime.now()
            # if game ends
            elif before.game:
                try:
                    end_time = datetime.datetime.now()
                    total_time = end_time - start_time[after.id].get(str(before.game), 0)
                    ranks[after.id][str(before.game)] = (ranks[after.id].get(str(before.game), 0)
                                                         + int(total_time.total_seconds()))
                    start_time[after.id][str(before.game)] = 0
                except TypeError:
                    pass


@client.event
async def on_message(message):
    # message evaluation
    msg = tuple(message.content.split())
    if "nlb.help" in msg and len(msg) == 1:
        await client.send_message(message.channel, "command:\t'rank [amount=5]'")
    elif "rank" in msg and len(msg) <= 2:
        amount = 5
        if msg[1].isdigit():
            amount = int(msg[1])
        # save times from current status
        for member in start_time.items():
            for status, time in member[1].items():
                if time != 0:
                    end_time = datetime.datetime.now()
                    total_time = end_time - start_time[member[0]].get(status, 0)
                    ranks[member[0]][status] = (ranks[member[0]].get(status, 0) + int(total_time.total_seconds()))
                    start_time[member[0]][status] = datetime.datetime.now()
        # print member rank
        sorted_ranks = sorted(ranks.items(), key=lambda x: x[1].get("Online", 0), reverse=True)
        i = 1
        for member in sorted_ranks:
            # for member on this server
            if message.server.get_member(member[0]):
                if i <= amount:
                    embed = discord.Embed(title="{}\t{}".format(i, message.server.get_member(member[0]).display_name),
                                          color=discord.Colour.red())
                    for j, (status, time) in enumerate(sorted(member[1].items(), key=lambda x: x[1], reverse=True), 1):
                        if j <= 5:
                            hours = 0
                            minutes = 0
                            seconds = time
                            if seconds >= 60:
                                minutes, seconds = divmod(seconds, 60)
                            if minutes >= 60:
                                hours, minutes = divmod(minutes, 60)
                            embed.add_field(name=status,
                                            value="{}:{}:{}"
                                            .format(str(hours).zfill(2), str(minutes).zfill(2), str(seconds).zfill(2)),
                                            inline=False)
                    await client.send_message(message.channel, embed=embed)
                    i += 1


client.run(os.getenv("TOKEN"))
