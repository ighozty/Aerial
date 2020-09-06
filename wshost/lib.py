"""AerialLib v1"""
import fortnitepy
import json
import asyncio
from functools import partial


class Client(fortnitepy.Client):
    def __init__(self, details: dict, ws):
        self.ws = ws

        super().__init__(
            auth=fortnitepy.DeviceAuth(**details),
        )

    async def cleanup(self):
        if self.is_ready():

            for f in self.friends:
                await f.remove()

            for r in self.pending_friends:
                if type(r) == fortnitepy.IncomingPendingFriend:
                    await r.decline()
                elif type(r) == fortnitepy.OutgoingPendingFriend:
                    await r.cancel()

            await self.set_presence("Battle Royale Lobby - 1 / 16")

            await self.party.me.edit_and_keep(
                partial(
                    self.party.me.set_outfit, "CID_565_Athena_Commando_F_RockClimber"
                ),
                partial(self.party.me.set_backpack, "BID_122_HalloweenTomato"),
                partial(
                    self.party.me.set_banner,
                    icon="otherbanner31",
                    color="defaultcolor3",
                    season_level=1337,
                ),
            )

            self.set_avatar(
                fortnitepy.Avatar(
                    asset="CID_565_Athena_Commando_F_RockClimber",
                    background_colors=["7c0dc8", "b521cc", "ed34d0"],
                )
            )

    async def event_ready(self):
        await self.cleanup()

    async def event_before_close(self):
        await self.cleanup()

    async def event_friend_request(self, request):
        if type(request) == fortnitepy.IncomingPendingFriend:
            await self.ws.send(
                json.dumps(
                    {
                        "type": "incoming_fr",
                        "name": request.display_name,
                        "id": request.id,
                    }
                )
            )

    async def event_party_invite(self, invitation: fortnitepy.ReceivedPartyInvitation):
        await self.ws.send(
            json.dumps(
                {
                    "type": "incoming_pi",
                    "name": invitation.sender.display_name,
                    "id": invitation.party.id,
                }
            )
        )


async def delay_stop(bot: Client, delay: float):
    await asyncio.sleep(delay)
    await bot.ws.send(
        json.dumps(
            {
                "type": "shutdown",
                "content": "You have reached the 90 minute limit per session. Start a new bot to continue usage.",
            }
        )
    )
    await bot.ws.close(code=4002, reason="Time Limit Reached")


async def process(bot: Client, cmd: dict):
    if cmd["type"] == "accept_fr":
        friend = bot.get_incoming_pending_friend(cmd["id"])
        if friend is not None:
            await friend.accept()
    elif cmd["type"] == "decline_fr":
        friend = bot.get_incoming_pending_friend(cmd["id"])
        if friend is not None:
            await friend.decline()
    elif cmd["type"] == "send_fr":
        user = await bot.fetch_profile(cmd["username"])
        if user is None:
            await bot.ws.send(
                json.dumps(
                    {
                        "type": "fail",
                        "action": "send_fr",
                        "reason": "not_found",
                        "username": cmd["username"],
                    }
                )
            )
            return
        try:
            await bot.add_friend(user.id)
            await bot.ws.send(
                json.dumps(
                    {
                        "type": "success",
                        "action": "send_fr",
                        "username": cmd["username"],
                    }
                )
            )
        except fortnitepy.Forbidden:
            await bot.ws.send(
                json.dumps(
                    {
                        "type": "fail",
                        "action": "send_fr",
                        "reason": "forbidden",
                        "username": cmd["username"],
                    }
                )
            )
        except:
            pass
    elif cmd["type"] == "del_f":
        user = await bot.fetch_profile(cmd["username"])
        if user is None:
            await bot.ws.send(
                json.dumps(
                    {
                        "type": "fail",
                        "action": "del_f",
                        "reason": "not_found",
                        "username": cmd["username"],
                    }
                )
            )
            return
        user = bot.get_friend(user.id)
        if user is None:
            await bot.ws.send(
                json.dumps(
                    {
                        "type": "fail",
                        "action": "del_f",
                        "reason": "not_friends",
                        "username": cmd["username"],
                    }
                )
            )
            return
        user.remove()
        await bot.ws.send(
            json.dumps(
                {"type": "success", "action": "del_f", "username": cmd["username"]}
            )
        )
    elif cmd["type"] == "accept_pi":
        try:
            await bot.join_party(cmd["id"])
            await bot.ws.send(json.dumps({"type": "success", "action": "accept_pi"}))
        except:
            await bot.ws.send(json.dumps({"type": "fail", "action": "accept_pi"}))
    elif cmd["type"] == "send_pi":
        user = await bot.fetch_profile(cmd["username"])
        if user is None:
            await bot.ws.send(
                json.dumps(
                    {
                        "type": "fail",
                        "action": "send_pi",
                        "reason": "not_found",
                        "username": cmd["username"],
                    }
                )
            )
            return
        user = bot.get_friend(user.id)
        if user is None:
            await bot.ws.send(
                json.dumps(
                    {
                        "type": "fail",
                        "action": "send_pi",
                        "reason": "not_friends",
                        "username": cmd["username"],
                    }
                )
            )
            return
        await user.invite()
        await bot.ws.send(
            json.dumps(
                {"type": "success", "action": "send_pi", "username": cmd["username"]}
            )
        )
    elif cmd["type"] == "set_status":
        await bot.set_presence(cmd["value"])
    elif cmd["type"] == "clone":
        user = await bot.fetch_profile(cmd["username"])
        if user is None:
            await bot.ws.send(
                json.dumps(
                    {
                        "type": "fail",
                        "action": "clone",
                        "reason": "not_found",
                        "username": cmd["username"],
                    }
                )
            )
            return
        user = bot.party.get_member(user.id)
        if user is None:
            await bot.ws.send(
                json.dumps(
                    {
                        "type": "fail",
                        "action": "clone",
                        "reason": "not_in_party",
                        "username": cmd["username"],
                    }
                )
            )
            return
        await bot.party.me.edit_and_keep(
            partial(
                bot.party.me.set_outfit,
                asset=user.outfit,
                variants=user.outfit_variants,
            ),
            partial(
                bot.party.me.set_backpack,
                asset=user.backpack,
                variants=user.backpack_variants,
            ),
            partial(
                bot.party.me.set_pickaxe,
                asset=user.pickaxe,
                variants=user.pickaxe_variants,
            ),
            partial(
                bot.party.me.set_banner,
                icon=user.banner[0],
                color=user.banner[1],
                season_level=user.banner[2],
            ),
            partial(
                bot.party.me.set_battlepass_info,
                has_purchased=user.battlepass_info[0],
                level=user.battlepass_info[1],
                self_boost_xp=user.battlepass_info[2],
                friend_boost_xp=user.battlepass_info[3],
            ),
        )
        await bot.ws.send(
            json.dumps(
                {"type": "success", "action": "clone", "username": cmd["username"]}
            )
        )
    elif cmd["type"] == "cosmetic_action":
        if cmd["item"] == "outfit":
            await bot.party.me.edit_and_keep(
                partial(bot.party.me.set_outfit, cmd["value"])
            )
            await bot.ws.send(
                json.dumps(
                    {
                        "type": "account_info",
                        "username": bot.user.display_name,
                        "outfit": bot.party.me.outfit,
                    }
                )
            )
        elif cmd["item"] == "backbling":
            if cmd.get("value") is None:
                await bot.party.me.clear_backpack()
            else:
                await bot.party.me.edit_and_keep(
                    partial(bot.party.me.set_backpack, cmd["value"])
                )
        elif cmd["item"] == "harvesting_tool":
            await bot.party.me.edit_and_keep(
                partial(bot.party.me.set_pickaxe, cmd["value"])
            )
        elif cmd["item"] == "emote":
            await bot.party.me.clear_emote()
            if cmd.get("value") is not None:
                await bot.party.me.edit_and_keep(
                    partial(bot.party.me.set_emote, cmd["value"])
                )
        elif cmd["item"] == "emoji":
            await bot.party.me.edit_and_keep(
                partial(bot.party.me.set_emoji, cmd["value"])
            )
        elif cmd["item"] == "banner":
            await bot.party.me.edit_and_keep(
                partial(
                    bot.party.me.set_banner,
                    icon=cmd.get("icon", bot.party.me.banner[0]),
                    color=cmd.get("color", bot.party.me.banner[1]),
                    season_level=cmd.get("season_level", bot.party.me.banner[2]),
                )
            )
        elif cmd["item"] == "battlepass":
            await bot.party.me.edit_and_keep(
                partial(
                    bot.party.me.set_battlepass_info,
                    has_purchased=cmd.get(
                        "has_purchased", bot.party.me.battlepass_info[0]
                    ),
                    level=cmd.get("level", bot.party.me.battlepass_info[1]),
                    self_boost_xp=cmd.get(
                        "self_boost_xp", bot.party.me.battlepass_info[2]
                    ),
                    friend_boost_xp=cmd.get(
                        "friend_boost_xp", bot.party.me.battlepass_info[3]
                    ),
                )
            )
        elif cmd["item"] == "variant":
            variants = bot.party.me.create_variants(**cmd["payload"])
            if cmd["cosmetic"] == "outfit":
                await bot.party.me.edit_and_keep(
                    partial(bot.party.me.set_outfit, variants=variants)
                )
            elif cmd["cosmetic"] == "backbling":
                await bot.party.me.edit_and_keep(
                    partial(bot.party.me.set_backpack, variants=variants)
                )
            elif cmd["cosmetic"] == "pet":
                await bot.party.me.edit_and_keep(
                    partial(bot.party.me.set_pet, variants=variants)
                )
            elif cmd["cosmetic"] == "harvesting_tool":
                await bot.party.me.edit_and_keep(
                    partial(bot.party.me.set_pickaxe, variants=variants)
                )
        elif cmd["item"] == "enlightenment":
            if cmd["cosmetic"] == "outfit":
                await bot.party.me.edit_and_keep(
                    partial(
                        bot.party.me.set_outfit,
                        variants=bot.party.me.outfit_variants,
                        enlightenment=cmd["payload"],
                    )
                )
            elif cmd["cosmetic"] == "backbling":
                await bot.party.me.edit_and_keep(
                    partial(
                        bot.party.me.set_backpack,
                        variants=bot.party.me.backpack_variants,
                        enlightenment=cmd["payload"],
                    )
                )
        elif cmd["item"] == "platform":
            bot.platform = cmd["value"]
            await bot.restart()
    elif cmd["type"] == "party_action":
        if cmd["action"] == "set_ready_state":
            if cmd["value"] == 0:
                await bot.party.me.set_ready(fortnitepy.ReadyState.NOT_READY)
            elif cmd["value"] == 1:
                await bot.party.me.set_ready(fortnitepy.ReadyState.READY)
            elif cmd["value"] == 2:
                await bot.party.me.set_ready(fortnitepy.ReadyState.SITTING_OUT)
        elif cmd["action"] == "leave":
            await bot.party.me.leave()
        elif cmd["action"] == "send_msg":
            await bot.party.send(cmd["content"])
        elif not bot.party.me.leader:
            await bot.ws.send(json.dumps({"type": "fail", "reason": "not_leader"}))
        elif cmd["action"] == "set_playlist":
            await bot.party.set_playlist(cmd["value"])
            await bot.ws.send(
                json.dumps(
                    {"type": "success", "action": "set_playlist", "value": cmd["value"]}
                )
            )
        elif cmd["action"] == "kick":
            user = await bot.fetch_profile(cmd["username"])
            if user is None:
                await bot.ws.send(
                    json.dumps(
                        {
                            "type": "fail",
                            "action": "kick",
                            "reason": "not_found",
                            "username": cmd["username"],
                        }
                    )
                )
                return
            user = bot.party.get_member(user.id)
            if user is None:
                await bot.ws.send(
                    json.dumps(
                        {
                            "type": "fail",
                            "action": "kick",
                            "reason": "not_in_party",
                            "username": cmd["username"],
                        }
                    )
                )
                return
            await user.kick()
            await bot.ws.send(
                json.dumps(
                    {"type": "success", "action": "kick", "username": cmd["username"]}
                )
            )
        elif cmd["action"] == "promote":
            user = await bot.fetch_profile(cmd["username"])
            if user is None:
                await bot.ws.send(
                    json.dumps(
                        {
                            "type": "fail",
                            "action": "promote",
                            "reason": "not_found",
                            "username": cmd["username"],
                        }
                    )
                )
                return
            user = bot.party.get_member(user.id)
            if user is None:
                await bot.ws.send(
                    json.dumps(
                        {
                            "type": "fail",
                            "action": "promote",
                            "reason": "not_in_party",
                            "username": cmd["username"],
                        }
                    )
                )
                return
            await user.promote()
            await bot.ws.send(
                json.dumps(
                    {
                        "type": "success",
                        "action": "promote",
                        "username": cmd["username"],
                    }
                )
            )
        elif cmd["action"] == "join":
            user = await bot.fetch_profile(cmd["username"])
            if user is None:
                await bot.ws.send(
                    json.dumps(
                        {
                            "type": "fail",
                            "action": "join",
                            "reason": "not_found",
                            "username": cmd["username"],
                        }
                    )
                )
                return
            user = bot.get_friend(user.id)
            if user is None:
                await bot.ws.send(
                    json.dumps(
                        {
                            "type": "fail",
                            "action": "join",
                            "reason": "not_friends",
                            "username": cmd["username"],
                        }
                    )
                )
                return
            try:
                await user.join_party()
                await bot.ws.send(
                    json.dumps(
                        {
                            "type": "success",
                            "action": "join",
                            "username": cmd["username"],
                        }
                    )
                )
            except fortnitepy.errors.Forbidden:
                await bot.ws.send(
                    json.dumps(
                        {
                            "type": "fail",
                            "action": "join",
                            "reason": "private",
                            "username": cmd["username"],
                        }
                    )
                )
        elif cmd["action"] == "leave":
            await bot.party.me.leave()
    elif cmd["type"] == "restart":
        await bot.restart()
        await bot.wait_until_ready()
        await bot.ws.send(json.dumps({"type": "success", "action": "restart"}))
    elif cmd["type"] == "stop":
        await bot.close()
        await bot.ws.send(
            json.dumps(
                {"type": "shutdown", "content": "You requested the bot to shut down."}
            )
        )
        await bot.ws.close()
