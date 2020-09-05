import discord
import asyncio
import ssl
import websockets
import json
import requests
import logging as log
import handle
from yaml import safe_load
from discord.ext import commands

config = safe_load(open("config.yml", "r"))
cert = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT).load_verify_locations("ssl/cert.pem")
loop = asyncio.get_event_loop()
active = {}
client = commands.AutoShardedBot(
    command_prefix="a.",
    activity=discord.Streaming(
        platform="Twitch",
        name="Fortnite Bots",
        details="Fortnite Bots",
        game="Fortnite Bots",
        url="https://twitch.tv/andre4ik3",
    ),
)
log.basicConfig(
    filename="dclient.log",
    format="DClient @ %(asctime)s | %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=log.INFO,
)

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
        active[user.id] = ws
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
                    ).set_thumbnail(url=img)
                )
            elif cmd["type"] == "shutdown":
                await accmsg.edit(
                    embed=discord.Embed(
                        title="<:Offline:719321200098017330> Bot Offline",
                        description=cmd["content"],
                        color=0x747F8D,
                    )
                )
                active.pop(user.id)
                await ws.close(code=1000)
                return
            elif cmd["type"] == "fail" or cmd["type"] == "success":
                await handle.feedback(cmd, user)
            elif cmd["type"] == "incoming_fr" or cmd["type"] == "incoming_pi":
                await handle.incoming(cmd, user, client, ws)
            else:
                await user.send("```json\n" + json.dumps(cmd) + "```")

@client.event
async def on_message(message: discord.Message):
    if (type(message.channel) == discord.DMChannel) and (message.author.id in list(active.keys())):
        await handle.command(message, active[message.author.id])
    elif "+startbot" in message.content:
        await message.channel.send(message.author.mention + " *if you are trying to start Aerial, please do `a.start`!*", delete_after=4)
    else:
        await client.process_commands(message)

@client.command()
async def startbeta(ctx):
    if ctx.message.author.id in list(active.keys()):
        await ctx.send(
            embed=discord.Embed(title=":x: Bot Already Running!", color=0xE46B6B),
            delete_after=3,
        )
    else:
        await wsconnect(ctx.message.author)


loop.create_task(client.start(config["Token"]))
loop.run_forever()
