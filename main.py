import discord
import collections
import datetime
import os

ranks = collections.defaultdict(dict)
start = collections.defaultdict(dict)
client = discord.Client()


@client.event
async def on_ready():
    await client.change_presence(game=discord.Game(name="Stalking {} users//nlb.help".
                                                   format(len(tuple(client.get_all_members())))))
    # if online or in-game from beginning
    for member in client.get_all_members():
        if not member.bot:
            if str(member.status) != "offline":
                start[member.id]["Online"] = datetime.datetime.now()
            if member.game:
                start[member.id][str(member.game)] = datetime.datetime.now()


@client.event
async def on_member_update(before, after):
    if not after.bot:
        # if status changed
        if before.status != after.status:
            # if online
            if str(before.status) == "offline":
                start[after.id]["Online"] = datetime.datetime.now()
            # if offline from online
            elif str(after.status) == "offline":
                try:
                    end_time = datetime.datetime.now()
                    total_time = end_time - start[after.id].get("Online", 0)
                    ranks[after.id]["Online"] = ranks[after.id].get("Online", 0) + int(total_time.total_seconds())
                    start[after.id]["Online"] = 0
                except TypeError:
                    pass
        # if game changed
        if before.game != after.game:
            # if game changes
            if before.game and after.game:
                try:
                    end_time = datetime.datetime.now()
                    total_time = end_time - start[after.id].get(str(before.game), 0)
                    ranks[after.id][str(before.game)] = (ranks[after.id].get(str(before.game), 0)
                                                         + int(total_time.total_seconds()))
                    start[after.id][str(before.game)] = 0
                except TypeError:
                    pass
                finally:
                    start[after.id][str(after.game)] = datetime.datetime.now()
            # if game starts
            elif after.game:
                start[after.id][str(after.game)] = datetime.datetime.now()
            # if game ends
            elif before.game:
                try:
                    end_time = datetime.datetime.now()
                    total_time = end_time - start[after.id].get(str(before.game), 0)
                    ranks[after.id][str(before.game)] = (ranks[after.id].get(str(before.game), 0)
                                                         + int(total_time.total_seconds()))
                    start[after.id][str(before.game)] = 0
                except TypeError:
                    pass


@client.event
async def on_message(message):
    # save times from current status
    for member in start.items():
        for status, time in member[1].items():
            if time != 0:
                end_time = datetime.datetime.now()
                total_time = end_time - start[member[0]].get(status, 0)
                ranks[member[0]][status] = (ranks[member[0]].get(status, 0) + int(total_time.total_seconds()))
                start[member[0]][status] = datetime.datetime.now()
    sorted_ranks = sorted(ranks.items(), key=lambda x: x[1].get("Online", 0), reverse=True)
    # message evaluation
    msg = tuple(message.content.split())
    out = str()
    # if cmd help
    if "nlb.help" in msg and len(msg) == 1:
        await client.send_message(message.channel, "command:\t'rank [amount=5]'\t- gets ranks up to amount\n" +
                                                   "\t" * 6 + "'my.rank'" + "\t" * 5 + " - gets own stats")
    # if cmd rank
    elif "rank" in msg and len(msg) <= 2:
        amount = 5
        if len(msg) == 2 and msg[1].isdigit():
            amount = int(msg[1])
        # get embed
        i = 1
        for member in sorted_ranks:
            # for member on this server
            if message.server.get_member(member[0]):
                if i <= amount:
                    out += "\n\n**{}.\t{}**\n".format(i, message.server.get_member(member[0]).display_name)
                    for j, (status, time) in enumerate(sorted(member[1].items(), key=lambda x: x[1], reverse=True), 1):
                        if j <= 5:
                            hours = 0
                            minutes = 0
                            seconds = time
                            if seconds >= 60:
                                minutes, seconds = divmod(seconds, 60)
                            if minutes >= 60:
                                hours, minutes = divmod(minutes, 60)
                            out += ("\n{}:{}:{}\t**{}**"
                                    .format(str(hours).zfill(2), str(minutes).zfill(2), str(seconds).zfill(2), status))
                    i += 1
        # print embed
        embed = discord.Embed(title="TOP {}".format(amount), description=out, color=discord.Colour.red())
        await client.send_message(message.channel, embed=embed)
    # if cmd my rank
    elif "my.rank" in msg and len(msg) == 1:
        # get embed
        for status, time in ranks.get(message.author.id).items():
            hours = 0
            minutes = 0
            seconds = time
            if seconds >= 60:
                minutes, seconds = divmod(seconds, 60)
            if minutes >= 60:
                hours, minutes = divmod(minutes, 60)
            out += ("\n{}:{}:{}\t**{}**"
                    .format(str(hours).zfill(2), str(minutes).zfill(2), str(seconds).zfill(2), status))
        # print embed
        embed = discord.Embed(title="{}".format(message.author.display_name), description=out, color=discord.Colour.red())
        await client.send_message(message.channel, embed=embed)


client.run(os.getenv("TOKEN"))
