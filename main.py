import discord
from collections import defaultdict
from datetime import datetime
import os

times = defaultdict(dict)
start = defaultdict(dict)

client = discord.Client()


@client.event
async def on_ready():
    await client.change_presence(game=discord.Game(name="ts.help//Stalking {} users".
                                                   format(len(tuple(client.get_all_members())))))
    # if online or in-game from beginning
    for member in client.get_all_members():
        if not member.bot:
            if str(member.status) != "offline":
                start[member.id]["Online"] = datetime.now()
            if member.game:
                start[member.id][str(member.game)] = datetime.now()


@client.event
async def on_member_update(before, after):
    await client.change_presence(game=discord.Game(name="ts.help//Stalking {} users".
                                                   format(len(tuple(client.get_all_members())))))
    if not after.bot:
        # if status changed
        if before.status != after.status:
            # if online
            if str(before.status) == "offline":
                start[after.id]["Online"] = datetime.now()
            # if offline from online
            elif str(after.status) == "offline":
                try:
                    end_time = datetime.now()
                    total_time = end_time - start[after.id].get("Online", 0)
                    times[after.id]["Online"] = times[after.id].get("Online", 0) + int(total_time.total_seconds())
                    start[after.id]["Online"] = 0
                except TypeError:
                    pass

        # if game changed
        if before.game != after.game:
            # if game changes
            if before.game and after.game:
                try:
                    end_time = datetime.now()
                    total_time = end_time - start[after.id].get(str(before.game), 0)
                    times[after.id][str(before.game)] = (times[after.id].get(str(before.game), 0)
                                                         + int(total_time.total_seconds()))
                    start[after.id][str(before.game)] = 0
                except TypeError:
                    pass
                finally:
                    start[after.id][str(after.game)] = datetime.now()
            # if game starts
            elif after.game:
                start[after.id][str(after.game)] = datetime.now()
            # if game ends
            elif before.game:
                try:
                    end_time = datetime.now()
                    total_time = end_time - start[after.id].get(str(before.game), 0)
                    times[after.id][str(before.game)] = (times[after.id].get(str(before.game), 0)
                                                         + int(total_time.total_seconds()))
                    start[after.id][str(before.game)] = 0
                except TypeError:
                    pass


@client.event
async def on_message(message):
    if message.content.startswith("ts."):
        msg = message.content.replace("ts.", "", 1)
        out = str()

        if len(msg.split()) == 1:
            # save times from current status
            for user_id, user_stats in start.items():
                if message.server.get_member(user_id):
                    for status, time in user_stats.items():
                        if time != 0:
                            end_time = datetime.now()
                            total_time = end_time - start[user_id].get(status, 0)
                            times[user_id][status] = times[user_id].get(status, 0) + int(total_time.total_seconds())
                            start[user_id][status] = datetime.now()

            # if cmd help
            if "help" in msg and len(msg) == 4:
                out = ("command:\t'ts.top'" + "\t" * 5 + "  - gets time stats of top 5 members\n" +
                       "\t" * 6 + "'ts.top[amount]'" + "\t- gets time stats of top amount members\n" +
                       "\t" * 6 + "'ts.self' " + "\t" * 5 + " - gets own time stats\n" +
                       "\t" * 6 + "'ts.username' " + "\t" * 2 + " - gets time stats of specific member")
                await client.send_message(message.channel, out)

            # if cmd top
            elif "top" in msg:
                # get amount
                msg = msg.replace("top", "", 1)
                if msg.isdigit() or not msg:
                    if msg.isdigit():
                        amount = int(msg)
                    else:
                        amount = 5
                    # get embed
                    i = 1
                    for user_id, user_stats in sorted(times.items(), key=lambda x: x[1].get("Online", 0), reverse=True):
                        # for member on this server
                        if message.server.get_member(user_id) and i <= amount:
                            out += "\n\n**{}.\t{}**\n".format(i, message.server.get_member(user_id).display_name)
                            for j, (status, time) in enumerate(sorted(user_stats.items(), key=lambda x: x[1],
                                                                      reverse=True), 1):
                                hours = 0
                                minutes = 0
                                seconds = time
                                if seconds >= 60:
                                    minutes, seconds = divmod(seconds, 60)
                                if minutes >= 60:
                                    hours, minutes = divmod(minutes, 60)
                                out += ("\n{}:{}:{}\t**{}**".format(str(hours).zfill(2), str(minutes).zfill(2),
                                                                    str(seconds).zfill(2), status))
                                if j == 5:
                                    break
                            # print embed
                            if i % 10 == 0:
                                embed = discord.Embed(title="TOP {}".format(amount), description=out[:2040],
                                                      color=discord.Colour.red())
                                await client.send_message(message.channel, embed=embed)
                                out = str()
                            i += 1
                    # print remaining embed
                    if out:
                        embed = discord.Embed(title="TOP {}".format(amount), description=out[:2040],
                                              color=discord.Colour.red())
                        await client.send_message(message.channel, embed=embed)

            # if cmd self
            elif "self" in msg and len(msg) == 4:
                # get embed
                for i, (status, time) in enumerate(sorted(times.get(message.author.id).items(),
                                                          key=lambda x: x[1], reverse=True), 1):
                    hours = 0
                    minutes = 0
                    seconds = time
                    if seconds >= 60:
                        minutes, seconds = divmod(seconds, 60)
                    if minutes >= 60:
                        hours, minutes = divmod(minutes, 60)
                    out += ("\n{}:{}:{}\t**{}**".format(str(hours).zfill(2), str(minutes).zfill(2),
                                                        str(seconds).zfill(2), status))
                    if i == 50:
                        break
                # print embed
                embed = discord.Embed(title="{}".format(message.author.display_name), description=out[:2040],
                                      color=discord.Colour.red())
                await client.send_message(message.channel, embed=embed)

            # if cmd user
            elif message.server.get_member_named(msg):
                user_id = message.server.get_member_named(msg).id
                # get embed
                for i, (status, time) in enumerate(sorted(times.get(user_id).items(), key=lambda x: x[1],
                                                          reverse=True), 1):
                    hours = 0
                    minutes = 0
                    seconds = time
                    if seconds >= 60:
                        minutes, seconds = divmod(seconds, 60)
                    if minutes >= 60:
                        hours, minutes = divmod(minutes, 60)
                    out += ("\n{}:{}:{}\t**{}**".format(str(hours).zfill(2), str(minutes).zfill(2),
                                                        str(seconds).zfill(2), status))
                    if i == 50:
                        break
                # print embed
                embed = discord.Embed(title="{}".format(message.server.get_member(user_id).display_name),
                                      description=out[:2040], color=discord.Colour.red())
                await client.send_message(message.channel, embed=embed)


client.run(os.getenv("TOKEN"))
