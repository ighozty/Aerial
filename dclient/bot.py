import discord
import asyncio
import ssl
import websockets
import json
import requests
import logging as log
import handle
from yaml import safe_load
from mysql.connector import connect as dbconnect
from discord.ext import commands
from discord.ext import tasks

config = safe_load(open("config.yml", "r"))
cert = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT).load_verify_locations("ssl/cert.pem")
active = {}
using = {}
client = commands.AutoShardedBot(
    command_prefix=["a.", "A."],
    case_insensitive=True,
    help_command=None,
)
db = dbconnect(
    host=config["Database"]["Host"],
    port=config["Database"]["Port"],
    user=config["Database"]["Username"],
    password=config["Database"]["Password"],
    database="aerial",
)
db.autocommit = True
log.basicConfig(
    filename="dclient.log",
    format="DClient @ %(asctime)s | %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=log.INFO,
)

# Check WebSocket Connection
async def wswait(accmsg: discord.Message):
    await asyncio.sleep(10)
    if type(accmsg.edited_at) is None:
        await accmsg.edit(
            embed=discord.Embed(
                title="<:Offline:719321200098017330> Bot Offline",
                description="Cannot establish a WebSocket connection.\nThis is likely because the server is offline.",
                color=0x747F8D,
            )
        )
        await active[accmsg.author.id].close(code=1000, reason="Timeout")
        active.pop(accmsg.channel.recipient.id, None)
        using.pop(accmsg.channel.recipient.id, None)


# Boost Check
async def is_boosting(id: int):
    g = client.get_guild(71884230999880502)
    member = g.get_member(id)
    if member is None:
        return False
    elif member in g.premium_subscribers:
        return True
    else:
        return False


# Main WebSocket Handler
async def wsconnect(user):
    try:
        accmsg = await user.send(
            embed=discord.Embed(
                title="<a:Loading:719025775042494505> Starting Bot...",
                color=0x7289DA,
            )
        )
    except discord.Forbidden:
        return
    async with websockets.connect(config["WSHost"], ssl=cert) as ws:
        if active.get(user.id, None) is None:
            active[user.id] = [ws]
        else:
            active[user.id].append(ws)
        asyncio.get_event_loop().create_task(wswait(accmsg))
        try:
            async for message in ws:
                cmd = json.loads(message)
                if cmd["type"] == "account_info":
                    r = requests.get(
                        "https://benbotfn.tk/api/v1/cosmetics/br/" + cmd["outfit"]
                    )
                    img = r.json().get("icons", {}).get("icon", "")
                    await accmsg.edit(
                        embed=discord.Embed(
                            title="<:Online:719038976677380138> " + cmd["username"],
                            color=0xFC5FE2,
                        )
                        .set_thumbnail(url=img)
                        .add_field(
                            name="Discord Server", value="https://discord.gg/fn8UfRY"
                        )
                        .add_field(name="Documentation", value="https://aerial.now.sh/")
                    )
                elif cmd["type"] == "shutdown":
                    await accmsg.edit(
                        embed=discord.Embed(
                            title="<:Offline:719321200098017330> Bot Offline",
                            description=cmd["content"],
                            color=0x747F8D,
                        )
                    )
                    active.get(user.id, []).remove(ws)
                    if active.get(user.id, []) == []:
                        active.pop(user.id, None)
                    return
                elif cmd["type"] == "fail" or cmd["type"] == "success":
                    await handle.feedback(cmd, user)
                elif cmd["type"] == "incoming_fr" or cmd["type"] == "incoming_pi":
                    await handle.incoming(cmd, user, client, ws)
                else:
                    await user.send("```json\n" + json.dumps(cmd) + "```")
        except websockets.exceptions.ConnectionClosedError:
            pass
    await accmsg.edit(
        embed=discord.Embed(
            title="<:Offline:719321200098017330> Bot Offline",
            description="The WebSocket connection was lost.",
            color=0x747F8D,
        )
    )
    active.get(user.id, []).remove(ws)
    if active.get(user.id, []) == []:
        active.pop(user.id, None)
    return


@client.event
async def on_message(message: discord.Message):
    if (type(message.channel) == discord.DMChannel) and (
        message.author.id in list(active.keys())
    ):
        for ws in active[message.author.id]:
            await handle.command(message, ws)
    elif message.channel.id == 718979003968520283 and "start" in message.content:
        if message.author.id in list(active.keys()):
            await message.author.send(
                embed=discord.Embed(title=":x: Bot Already Running!", color=0xE46B6B),
                delete_after=10,
            )
        else:
            await wsconnect(message.author)
    else:
        await client.process_commands(message)


@client.command(aliases=["startbot", "create"])
async def start(ctx):
    if ctx.message.author.id in list(active.keys()):
        await ctx.message.author.send(
            embed=discord.Embed(title=":x: Bot Already Running!", color=0xE46B6B),
            delete_after=10,
        )
    # elif len(active.get(ctx.message.author.id, [])) >= 3:
    #    await ctx.message.author.send(
    #        embed=discord.Embed(title=":x: Account Limit Reached!", color=0xE46B6B),
    #        delete_after=10,
    #    )
    else:
        await wsconnect(ctx.message.author)


@client.command(aliases=["stop"])
async def kill(ctx):
    if ctx.message.author.id in list(active.keys()):
        for ws in active[ctx.message.author.id]:
            await ws.send(json.dumps({"type": "stop"}))
        await ctx.channel.send(
            f"<:Accept:719047548219949136> {ctx.message.author.mention} Sent shutdown request to bot!"
        )
    else:
        await ctx.channel.send(
            f"<:Reject:719047548819472446> {ctx.message.author.mention} You do not have an active bot! Type `a.start` to create one!"
        )


@client.command()
async def help(ctx):
    commands = {
        "start": "Starts the bot for 3 hours.",
        "kill": "Stops the bot outside of DMs.",
        "help": "Shows this message.",
    }
    cmdlist = ""
    for c in commands:
        cmdlist = f"{cmdlist}`{c}` - {commands[c]}\n"
    await ctx.send(
        embed=discord.Embed(
            title="Aerial Commands", description=cmdlist, color=0xFC5FE2
        ).set_footer(text="Support Server: https://discord.gg/fn8UfRY")
    )


@tasks.loop(minutes=5.0)
async def counter():
    c1 = await client.fetch_channel(727599283179749466)
    c2 = await client.fetch_channel(720787276329910363)
    c = db.cursor()
    c.execute("""SELECT COUNT(*) FROM `accounts` WHERE `in_use` = '1';""")
    running = c.fetchone()[0]
    c.execute("""SELECT COUNT(*) FROM `accounts`;""")
    all = c.fetchone()[0]
    name1 = f"{len(client.guilds)} Servers"
    name2 = f"{running}/{all} Clients Running"
    await c1.edit(name=name1)
    await c2.edit(name=name2)


@counter.before_loop
async def before_counter():
    await client.wait_until_ready()


@client.event
async def on_ready():
    counter.start()


@client.event
async def on_shard_ready(shard_id: int):
    await client.change_presence(
        activity=discord.Streaming(
            platform="Twitch",
            name=f"Fortnite Bots | SH{shard_id}",
            url="https://twitch.tv/andre4ik3",
        ),
        shard_id=shard_id,
    )


if __name__ == "__main__":
    client.run(config["Token"])
    users = list(active.values())
    for u in users:
        for ws in active[u]:
            asyncio.get_event_loop().create_task(ws.close())
