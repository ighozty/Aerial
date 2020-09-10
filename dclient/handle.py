import discord
import json
import requests
import asyncio


def cosmetic(name_or_id: str, type: str = None):
    if name_or_id.startswith(("CID_", "BID_", "EID_", "Emoji_", "Pickaxe_ID_")):
        item = requests.get("https://benbotfn.tk/api/v1/cosmetics/br/" + name_or_id)

        if item.status_code == 404:
            return {"name": name_or_id, "id": name_or_id}
        else:
            return item.json()

    else:
        item = requests.get(
            "https://benbotfn.tk/api/v1/cosmetics/br/search",
            params={
                "lang": "en",
                "searchLang": "en",
                "matchMethod": "contains",
                "name": name_or_id,
                "backendType": type,
            },
        )

        if item.status_code != 200:
            return None
        else:
            return item.json()


def convert(ls: list):
    return {ls[i]: ls[i + 1] for i in range(0, len(ls), 2)}


async def feedback(cmd: dict, user):
    if cmd["type"] == "success":
        if cmd["action"] == "send_fr":
            await user.send(
                "<:Accept:719047548219949136> Sent Friend Request to "
                + cmd["username"],
                delete_after=10,
            )
        elif cmd["action"] == "del_f":
            await user.send(
                "<:Accept:719047548219949136> Removed " + cmd["username"],
                delete_after=10,
            )
        elif cmd["action"] == "send_pi":
            await user.send(
                "<:Accept:719047548219949136> Sent Invite to " + cmd["username"],
                delete_after=10,
            )
        elif cmd["action"] == "clone":
            await user.send(
                "<:Accept:719047548219949136> Cloned " + cmd["username"],
                delete_after=10,
            )
        elif cmd["action"] == "hide":
            await user.send(
                "<:Accept:719047548219949136> Hidden " + cmd["username"],
                delete_after=10,
            )
        elif cmd["action"] == "unhide":
            await user.send(
                "<:Accept:719047548219949136> Showing " + cmd["username"],
                delete_after=10,
            )
        elif cmd["action"] == "set_playlist":
            await user.send(
                "<:Accept:719047548219949136> Set Playlist to " + cmd["value"],
                delete_after=10,
            )
        elif cmd["action"] == "kick":
            await user.send(
                "<:Accept:719047548219949136> Kicked " + cmd["username"],
                delete_after=10,
            )
        elif cmd["action"] == "promote":
            await user.send(
                "<:Accept:719047548219949136> Promoted " + cmd["username"],
                delete_after=10,
            )
    elif cmd["type"] == "fail":
        if cmd["reason"] == "not_found":
            await user.send(
                "<:Reject:719047548819472446> Cannot Find " + cmd["username"],
                delete_after=10,
            )
        elif cmd["reason"] == "forbidden":
            await user.send(
                "<:Reject:719047548819472446> Cannot Send Friend Request to "
                + cmd["username"],
                delete_after=10,
            )
        elif cmd["reason"] == "not_friends":
            await user.send(
                "<:Reject:719047548819472446> Not Friends with " + cmd["username"],
                delete_after=10,
            )
        elif cmd["reason"] == "not_found":
            await user.send(
                "<:Reject:719047548819472446> Cannot Find " + cmd["username"],
                delete_after=10,
            )
        elif cmd["reason"] == "not_leader":
            await user.send(
                "<:Reject:719047548819472446> This Action Requires the Bot to be Party Leader!",
                delete_after=10,
            )
        elif cmd["action"] == "accept_pi":
            await user.send(
                "<:Reject:719047548819472446> Cannot Join " + cmd["username"],
                delete_after=10,
            )


async def incoming(cmd: dict, user, dclient, ws):
    if cmd["type"] == "incoming_fr":
        rmsg = await user.send(
            embed=discord.Embed(
                title="<:FriendRequest:719042256849338429> Friend Request from "
                + cmd["name"],
                description="<:Accept:719047548219949136> Accept    <:Reject:719047548819472446> Reject",
            )
        )
        await rmsg.add_reaction(":Accept:719047548219949136")
        await rmsg.add_reaction(":Reject:719047548819472446")

        def check(reaction, user):
            if (
                str(reaction.emoji)
                in ["<:Accept:719047548219949136>", "<:Reject:719047548819472446>"]
                and not user.bot
            ):
                return True
            else:
                return False

        try:
            reaction, user = await dclient.wait_for(
                "reaction_add", timeout=60.0, check=check
            )
        except asyncio.TimeoutError:
            await rmsg.edit(
                delete_after=1,
                embed=discord.Embed(
                    title="<:FriendRequest:719042256849338429> Friend Request from "
                    + cmd["name"],
                    color=0xF24949,
                ),
            )
            await ws.send(json.dumps({"type": "decline_fr", "id": cmd["id"]}))

        else:
            if str(reaction.emoji) == "<:Accept:719047548219949136>":
                await rmsg.edit(
                    delete_after=1,
                    embed=discord.Embed(
                        title="<:FriendRequest:719042256849338429> Friend Request from "
                        + cmd["name"],
                        color=0x43B581,
                    ),
                )
                await ws.send(json.dumps({"type": "accept_fr", "id": cmd["id"]}))

            elif str(reaction.emoji) == "<:Reject:719047548819472446>":
                await rmsg.edit(
                    delete_after=1,
                    embed=discord.Embed(
                        title="<:FriendRequest:719042256849338429> Friend Request from "
                        + cmd["name"],
                        color=0xF24949,
                    ),
                )
                await ws.send(json.dumps({"type": "decline_fr", "id": cmd["id"]}))
    elif cmd["type"] == "incoming_pi":
        rmsg = await user.send(
            embed=discord.Embed(
                title="<:PartyInvite:719198827281645630> Party Invite from "
                + cmd["name"],
                description="<:Accept:719047548219949136> Accept    <:Reject:719047548819472446> Reject",
            )
        )

        await rmsg.add_reaction(":Accept:719047548219949136")
        await rmsg.add_reaction(":Reject:719047548819472446")

        def check(reaction, user):
            if (
                str(reaction.emoji)
                in ["<:Accept:719047548219949136>", "<:Reject:719047548819472446>"]
                and not user.bot
            ):
                return True
            else:
                return False

        try:
            reaction, user = await dclient.wait_for(
                "reaction_add", timeout=60.0, check=check
            )
        except asyncio.TimeoutError:
            await rmsg.edit(
                delete_after=1,
                embed=discord.Embed(
                    title="<:PartyInvite:719198827281645630> Party Invite from "
                    + cmd["name"],
                    color=0xF24949,
                ),
            )
            await ws.send(json.dumps({"type": "decline_pi", "id": cmd["id"]}))

        else:
            if str(reaction.emoji) == "<:Accept:719047548219949136>":
                await rmsg.edit(
                    delete_after=1,
                    embed=discord.Embed(
                        title="<:PartyInvite:719198827281645630> Party Invite from "
                        + cmd["name"],
                        color=0x43B581,
                    ),
                )
                await ws.send(json.dumps({"type": "accept_pi", "id": cmd["id"]}))

            elif str(reaction.emoji) == "<:Reject:719047548819472446>":
                await rmsg.edit(
                    delete_after=1,
                    embed=discord.Embed(
                        title="<:PartyInvite:719198827281645630> Party Invite from "
                        + cmd["name"],
                        color=0xF24949,
                    ),
                )
                await ws.send(json.dumps({"type": "decline_pi", "id": cmd["id"]}))


async def command(message: discord.Message, ws):
    msg = message.content.split(" ")
    if msg[0].lower() == "stop" or msg[0].lower() == "logout":
        await ws.send(json.dumps({"type": "stop"}))
    elif msg[0].lower() == "restart" or msg[0].lower() == "reboot":
        await ws.send(json.dumps({"type": "restart"}))
        await message.channel.send(
            content="<:Accept:719047548219949136> Restarted Bot",
            delete_after=10,
        )
    elif msg[0].lower() == "help":
        await message.channel.send(
            content="Documentation is available here: **<https://aerial.now.sh/>**",
            delete_after=10,
        )
    elif msg[0].lower() == "ready":
        await ws.send(
            json.dumps(
                {"type": "party_action", "action": "set_ready_state", "value": 1}
            )
        )
    elif msg[0].lower() == "unready" or msg[0].lower() == "sitin":
        await ws.send(
            json.dumps(
                {"type": "party_action", "action": "set_ready_state", "value": 0}
            )
        )
    elif msg[0].lower() == "sitout":
        await ws.send(
            json.dumps(
                {"type": "party_action", "action": "set_ready_state", "value": 2}
            )
        )
    elif msg[0].lower() == "leave":
        await ws.send(json.dumps({"type": "party_action", "action": "leave"}))
    elif msg[0].lower() == "promote":
        msg[1] = " ".join(msg[1:])
        await ws.send(
            json.dumps(
                {"type": "party_action", "action": "promote", "username": msg[1]}
            )
        )
    elif msg[0].lower() == "kick":
        msg[1] = " ".join(msg[1:])
        await ws.send(
            json.dumps({"type": "party_action", "action": "kick", "username": msg[1]})
        )
    elif msg[0].lower() == "join":
        msg[1] = " ".join(msg[1:])
        await ws.send(
            json.dumps({"type": "party_action", "action": "join", "username": msg[1]})
        )
    elif msg[0].lower() == "invite":
        msg[1] = " ".join(msg[1:])
        await ws.send(json.dumps({"type": "send_pi", "username": msg[1]}))
    elif msg[0].lower() == "hide":
        if len(msg) == 1:
            await ws.send(json.dumps({"type": "party_action", "action": "hide"}))
        else:
            msg[1] = " ".join(msg[1:])
            await ws.send(
                json.dumps(
                    {"type": "party_action", "action": "hide", "username": msg[1]}
                )
            )
    elif msg[0].lower() == "unhide":
        if len(msg) == 1:
            await ws.send(json.dumps({"type": "party_action", "action": "unhide"}))
        else:
            msg[1] = " ".join(msg[1:])
            await ws.send(
                json.dumps(
                    {"type": "party_action", "action": "unhide", "username": msg[1]}
                )
            )
    elif msg[0].lower() == "set":
        if len(msg) < 3:
            return
        elif msg[1].lower() == "outfit" or msg[1].lower() == "skin":
            msg[2] = " ".join(msg[2:])
            cosm = cosmetic(msg[2], "AthenaCharacter")
            if cosm is None:
                await message.channel.send(
                    "<:Reject:719047548819472446> Cannot Find Outfit " + msg[2],
                    delete_after=10,
                )
            else:
                await ws.send(
                    json.dumps(
                        {
                            "type": "cosmetic_action",
                            "item": "outfit",
                            "value": cosm["id"],
                        }
                    )
                )
                await message.channel.send(
                    "<:Accept:719047548219949136> Set Outfit to " + cosm["name"],
                    delete_after=10,
                )
        elif msg[1].lower() == "backbling" or msg[1].lower() == "backpack":
            msg[2] = " ".join(msg[2:])
            if msg[2].lower() == "none":
                await ws.send(
                    json.dumps({"type": "cosmetic_action", "item": "backbling"})
                )
                await message.channel.send(
                    "<:Accept:719047548219949136> Set Back Bling to None",
                    delete_after=10,
                )
            else:
                cosm = cosmetic(msg[2], "AthenaBackpack")
                if cosm is None:
                    await message.channel.send(
                        "<:Reject:719047548819472446> Cannot Find Back Bling " + msg[2],
                        delete_after=10,
                    )
                else:
                    await ws.send(
                        json.dumps(
                            {
                                "type": "cosmetic_action",
                                "item": "backbling",
                                "value": cosm["id"],
                            }
                        )
                    )
                    await message.channel.send(
                        "<:Accept:719047548219949136> Set Back Bling to "
                        + cosm["name"],
                        delete_after=10,
                    )
        elif msg[1].lower() == "emote" or msg[1].lower() == "dance":
            msg[2] = " ".join(msg[2:])
            if msg[2].lower() == "none":
                await ws.send(json.dumps({"type": "cosmetic_action", "item": "emote"}))
                await message.channel.send(
                    "<:Accept:719047548219949136> Set Emote to None", delete_after=10
                )
            else:
                cosm = cosmetic(msg[2], "AthenaDance")
                if cosm is None:
                    await message.channel.send(
                        "<:Reject:719047548819472446> Cannot Find Emote " + msg[2],
                        delete_after=10,
                    )
                else:
                    await ws.send(
                        json.dumps(
                            {
                                "type": "cosmetic_action",
                                "item": "emote",
                                "value": cosm["id"],
                            }
                        )
                    )
                    await message.channel.send(
                        "<:Accept:719047548219949136> Set Emote to " + cosm["name"],
                        delete_after=10,
                    )
        elif msg[1].lower() == "emoji" or msg[1].lower() == "emoticon":
            msg[2] = " ".join(msg[2:])
            cosm = cosmetic(msg[2], "AthenaEmoji")
            if cosm is None:
                await message.channel.send(
                    "<:Reject:719047548819472446> Cannot Find Emoji " + msg[2],
                    delete_after=10,
                )
            else:
                await ws.send(
                    json.dumps(
                        {
                            "type": "cosmetic_action",
                            "item": "emoji",
                            "value": cosm["id"],
                        }
                    )
                )
                await message.channel.send(
                    "<:Accept:719047548219949136> Set Emoji to " + cosm["name"],
                    delete_after=10,
                )
        elif (
            msg[1].lower() == "harvesting_tool"
            or msg[1].lower() == "harvestingtool"
            or msg[1].lower() == "pickaxe"
        ):
            msg[2] = " ".join(msg[2:])
            cosm = cosmetic(msg[2], "AthenaPickaxe")
            if cosm is None:
                await message.channel.send(
                    "<:Reject:719047548819472446> Cannot Find Harvesting Tool "
                    + msg[2],
                    delete_after=10,
                )
            else:
                await ws.send(
                    json.dumps(
                        {
                            "type": "cosmetic_action",
                            "item": "harvesting_tool",
                            "value": cosm["id"],
                        }
                    )
                )
                await message.channel.send(
                    "<:Accept:719047548219949136> Set Harvesting Tool to "
                    + cosm["name"],
                    delete_after=10,
                )
        elif msg[1].lower() == "banner" and len(msg) == 4:
            if msg[2].lower() == "design" or msg[2].lower() == "icon":
                await ws.send(
                    json.dumps(
                        {"type": "cosmetic_action", "item": "banner", "icon": msg[3]}
                    )
                )
                await message.channel.send(
                    "<:Accept:719047548219949136> Set Banner Design to " + msg[3],
                    delete_after=10,
                )
            elif msg[2].lower() == "color" or msg[2].lower() == "colour":
                await ws.send(
                    json.dumps(
                        {"type": "cosmetic_action", "item": "banner", "color": msg[3]}
                    )
                )
                await message.channel.send(
                    "<:Accept:719047548219949136> Set Banner Color to " + msg[3],
                    delete_after=10,
                )
            elif msg[2].lower() == "season_level" or msg[2].lower() == "level":
                await ws.send(
                    json.dumps(
                        {
                            "type": "cosmetic_action",
                            "item": "banner",
                            "season_level": msg[3],
                        }
                    )
                )
                await message.channel.send(
                    "<:Accept:719047548219949136> Set Season Level to " + msg[3],
                    delete_after=10,
                )
        elif msg[1].lower() == "battlepass" or msg[1].lower() == "bp" and len(msg) == 4:
            if msg[2].lower() == "has_purchased":
                if msg[3] == "true":
                    await ws.send(
                        json.dumps(
                            {
                                "type": "cosmetic_action",
                                "item": "battlepass",
                                "has_purchased": True,
                            }
                        )
                    )
                    await message.channel.send(
                        "<:Accept:719047548219949136> Set Battle Pass Purchase Status to True",
                        delete_after=10,
                    )
                elif msg[3] == "false":
                    await ws.send(
                        json.dumps(
                            {
                                "type": "cosmetic_action",
                                "item": "battlepass",
                                "has_purchased": False,
                            }
                        )
                    )
                    await message.channel.send(
                        "<:Accept:719047548219949136> Set Battle Pass Purchase Status to False",
                        delete_after=10,
                    )
            elif msg[2].lower() == "level":
                await ws.send(
                    json.dumps(
                        {
                            "type": "cosmetic_action",
                            "item": "battlepass",
                            "level": msg[3],
                        }
                    )
                )
                await message.channel.send(
                    "<:Accept:719047548219949136> Set Battle Pass Level to " + msg[3],
                    delete_after=10,
                )
            elif msg[2].lower() == "self_boost_xp":
                await ws.send(
                    json.dumps(
                        {
                            "type": "cosmetic_action",
                            "item": "battlepass",
                            "self_boost_xp": msg[3],
                        }
                    )
                )
                await message.channel.send(
                    "<:Accept:719047548219949136> Set Battle Pass Self Boost to "
                    + msg[3],
                    delete_after=10,
                )
            elif msg[2].lower() == "friend_boost_xp":
                await ws.send(
                    json.dumps(
                        {
                            "type": "cosmetic_action",
                            "item": "battlepass",
                            "friend_boost_xp": msg[3],
                        }
                    )
                )
                await message.channel.send(
                    "<:Accept:719047548219949136> Set Battle Pass Friend Boost to "
                    + msg[3],
                    delete_after=10,
                )
        elif msg[1].lower() == "status" or msg[1].lower() == "presence":
            msg[2] = " ".join(msg[2:])
            await ws.send(json.dumps({"type": "set_status", "value": msg[2]}))
            await message.channel.send(
                "<:Accept:719047548219949136> Set Status to " + msg[2], delete_after=10
            )
        elif (
            msg[1].lower() == "playlist"
            or msg[1].lower() == "gamemode"
            or msg[1].lower() == "mode"
        ):
            msg[2] = " ".join(msg[2:])
            await ws.send(
                json.dumps(
                    {"type": "party_action", "action": "set_playlist", "value": msg[2]}
                )
            )
        elif msg[1].lower() == "variants" or msg[1].lower() == "variant":
            variants = convert(msg[3:])
            if msg[2].lower() == "outfit" or msg[2].lower() == "skin":
                await ws.send(
                    json.dumps(
                        {
                            "type": "cosmetic_action",
                            "item": "variant",
                            "cosmetic": "outfit",
                            "payload": variants,
                        }
                    )
                )
                await message.channel.send(
                    "<:Accept:719047548219949136> Set Variants to " + str(variants),
                    delete_after=10,
                )
            elif msg[2].lower() == "backbling" or msg[2].lower() == "backpack":
                await ws.send(
                    json.dumps(
                        {
                            "type": "cosmetic_action",
                            "item": "variant",
                            "cosmetic": "backbling",
                            "payload": variants,
                        }
                    )
                )
                await message.channel.send(
                    "<:Accept:719047548219949136> Set Variants to " + str(variants),
                    delete_after=10,
                )
            elif (
                msg[2].lower() == "harvesting_tool"
                or msg[2].lower() == "harvestingtool"
                or msg[2].lower() == "pickaxe"
            ):
                await ws.send(
                    json.dumps(
                        {
                            "type": "cosmetic_action",
                            "item": "variant",
                            "cosmetic": "harvesting_tool",
                            "payload": variants,
                        }
                    )
                )
                await message.channel.send(
                    "<:Accept:719047548219949136> Set Variants to " + str(variants),
                    delete_after=10,
                )
        elif msg[1].lower() == "enlightenment" or msg[1].lower() == "enlighten":
            if msg[2].lower() == "outfit" or msg[2].lower() == "skin":
                await ws.send(
                    json.dumps(
                        {
                            "type": "cosmetic_action",
                            "item": "enlightenment",
                            "cosmetic": "outfit",
                            "payload": (msg[3], msg[4]),
                        }
                    )
                )
                await message.channel.send(
                    "<:Accept:719047548219949136> Set Enlightenment to Season "
                    + msg[3]
                    + " Level "
                    + msg[4],
                    delete_after=10,
                )
            elif msg[2].lower() == "backbling" or msg[2].lower() == "backpack":
                await ws.send(
                    json.dumps(
                        {
                            "type": "cosmetic_action",
                            "item": "enlightenment",
                            "cosmetic": "backbling",
                            "payload": (msg[3], msg[4]),
                        }
                    )
                )
                await message.channel.send(
                    "<:Accept:719047548219949136> Set Enlightenment to Season "
                    + msg[3]
                    + " Level "
                    + msg[4],
                    delete_after=10,
                )
            elif (
                msg[2].lower() == "harvesting_tool"
                or msg[2].lower() == "harvestingtool"
                or msg[2].lower() == "pickaxe"
            ):
                await ws.send(
                    json.dumps(
                        {
                            "type": "cosmetic_action",
                            "item": "enlightenment",
                            "cosmetic": "harvesting_tool",
                            "payload": (msg[3], msg[4]),
                        }
                    )
                )
                await message.channel.send(
                    "<:Accept:719047548219949136> Set Enlightenment to Season"
                    + msg[3]
                    + " Level "
                    + msg[4],
                    delete_after=10,
                )
        elif msg[1].lower() == "platform":
            if msg[2].lower() not in [
                "win",
                "windows",
                "pc",
                "mac",
                "xbox",
                "xbl",
                "ps4",
                "psn",
                "playstation",
                "switch",
                "swt",
                "nsw",
                "android",
                "and",
                "ios",
                "iphone",
                "mobile",
            ]:
                await message.channel.send(
                    "<:Reject:719047548819472446> Invalid Platform! Platform must be one of: ```\nWINDOWS, PC, MAC, XBOX, PS4, SWITCH, ANDROID, IOS```"
                )
                return
            else:
                await ws.send(
                    json.dumps(
                        {
                            "type": "cosmetic_action",
                            "item": "platform",
                            "value": msg[2].lower(),
                        }
                    )
                )
                await message.channel.send(
                    "<:Accept:719047548219949136> Set Platform to " + msg[2]
                )
    elif msg[0].lower() == "friend":
        msg[2] = " ".join(msg[2:])
        if msg[1].lower() == "add":
            await ws.send(json.dumps({"type": "send_fr", "username": msg[2]}))
        elif msg[1].lower() == "remove":
            await ws.send(json.dumps({"type": "del_f", "username": msg[2]}))
    elif msg[0].lower() == "send":
        msg[1] = " ".join(msg[1:])
        await ws.send(
            json.dumps(
                {"type": "party_action", "action": "send_msg", "content": msg[1]}
            )
        )
        await message.channel.send(
            "<:Accept:719047548219949136> Sent Party Message", delete_after=10
        )
    elif msg[0].lower() == "clone" or msg[0].lower() == "copy":
        msg[1] = " ".join(msg[1:])
        await ws.send(json.dumps({"type": "clone", "username": msg[1]}))
    elif msg[0].lower() == "variants":
        if len(msg) < 2:
            return
        cosm = cosmetic(" ".join(msg[1:]), "AthenaCharacter")
        if cosm is None:
            cosm = cosmetic(" ".join(msg[1:]), "AthenaBackpack")
            if cosm is None:
                cosm = cosmetic(" ".join(msg[1:]), "AthenaPickaxe")
                if cosm is None:
                    await message.channel.send(
                        "<:Reject:719047548819472446> Cannot Find Cosmetic " + msg[1]
                    )
                    return
        elif "variants" not in list(cosm.keys()):
            await message.channel.send(
                "<:Reject:719047548819472446> " + cosm["name"] + " has no variants"
            )
            return
        await message.channel.send(
            embed=discord.Embed(title="Variants for " + cosm["name"], type="rich")
            .set_thumbnail(url=cosm["icons"]["icon"])
            .add_field(
                name="Description",
                value=cosm["description"] + "\n" + cosm["setText"],
                inline=True,
            )
            .add_field(name="ID", value=cosm["id"], inline=True),
            delete_after=300,
        )
        for ch in cosm["variants"]:
            embed = discord.Embed(title=ch["channel"], type="rich")
            for st in ch["options"]:
                embed.add_field(name=st["tag"], value=st["name"], inline=True)
            await message.channel.send(embed=embed, delete_after=300)
    return True
